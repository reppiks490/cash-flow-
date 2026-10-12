import hashlib
import hmac
import json
import tempfile
import unittest
from pathlib import Path

from moneyfall.orders import Orders,verify_stripe


class OrdersTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Orders(Path(self.tmp.name)/'orders.sqlite',repo=Path.cwd())
        self.db.ingest(dict(id='one',company='Example',title='Public content',url='https://example.org',retrieved_at='now',attribution={'opportunity_id':'signal-driven-b2b'}))
        self.db.create_order('order-one','one',scope='3 graphics, 15-second preview, 3 captions, one revision',price_cents=14900)
    def tearDown(self):self.db.close();self.tmp.cleanup()
    def test_no_fulfillment_before_payment_and_licensed_assets(self):
        self.assertFalse(self.db.ready('order-one'))
        self.db.payment('order-one','receipt-one',14900)
        self.assertFalse(self.db.ready('order-one'))
        self.db.assets('order-one',licensed=True,reference='client-approved-brief')
        self.assertTrue(self.db.ready('order-one'))
    def test_replayed_payment_and_wrong_amount(self):
        with self.assertRaises(ValueError):self.db.payment('order-one','wrong',14899)
        self.assertTrue(self.db.payment('order-one','receipt',14900))
        self.assertFalse(self.db.payment('order-one','receipt',14900))
        with self.assertRaises(ValueError):self.db.payment('order-one','second',14900)
        self.assertEqual(self.db.metrics()['net_revenue_cents'],14900)
    def test_unknown_order_or_unlicensed_assets_rejected(self):
        with self.assertRaises(ValueError):self.db.payment('unknown','receipt',14900)
        with self.assertRaises(ValueError):self.db.assets('order-one',licensed=False,reference='unknown rights')
    def test_fulfillment_checks_manifest_not_only_directory_exists(self):
        with self.assertRaises(ValueError):self.db.fulfill('order-one',Path(self.tmp.name))

    def test_order_attribution_is_bound_at_scope_acceptance(self):
        self.db.ingest(dict(id='one',company='Example',title='Public content',url='https://example.org',retrieved_at='now',attribution={'opportunity_id':'different'}))
        self.db.payment('order-one','receipt',14900)
        self.assertEqual(self.db.metrics(opportunity_id='signal-driven-b2b')['net_revenue_cents'],14900)
        self.assertEqual(self.db.metrics(opportunity_id='different')['net_revenue_cents'],0)

    def test_refund_is_per_order_not_shared_signal_balance(self):
        self.db.create_order('order-two','one',scope='second approved kit',price_cents=14900)
        for ident in ('order-one','order-two'):
            self.db.payment(ident,'receipt-'+ident,14900)
            self.db.assets(ident,licensed=True,reference='approved')
        self.db.refund('order-one','refund-one',14900)
        self.assertFalse(self.db.ready('order-one'))
        self.assertTrue(self.db.ready('order-two'))

    def test_refund_receipt_cannot_be_reused_for_another_order(self):
        self.db.create_order('order-two','one',scope='second kit',price_cents=14900)
        for ident in ('order-one','order-two'):self.db.payment(ident,'paid-'+ident,14900)
        self.db.refund('order-one','unique-refund',14900)
        self.assertFalse(self.db.refund('order-one','unique-refund',14900))
        with self.assertRaises(ValueError):self.db.refund('order-two','unique-refund',14900)

    def test_another_orders_kit_cannot_be_fulfilled(self):
        self.db.payment('order-one','receipt',14900)
        self.db.assets('order-one',licensed=True,reference='approved')
        folder=Path(self.tmp.name)/'kit';folder.mkdir()
        files={}
        for name in ['proof.pdf','captions.md','motion-preview.mp4']+[f'card-{n:03}.{ext}' for n in (1,2,3) for ext in ('png','svg')]:
            (folder/name).write_bytes(b'not real media')
            files[name]=hashlib.sha256(b'not real media').hexdigest()
        (folder/'manifest.json').write_text(json.dumps({'order_id':'different','specimen':False,'files':files}))
        with self.assertRaises(ValueError):self.db.fulfill('order-one',folder)
        self.db.payment('order-one','receipt',14900)
        self.db.assets('order-one',licensed=True,reference='approved')
        with self.assertRaises(ValueError):self.db.fulfill('order-one',Path(self.tmp.name))


class WebhookTests(unittest.TestCase):
    def signed(self,payload,now=1000):
        raw=json.dumps(payload).encode()
        sig=hmac.new(b'synthetic-secret',str(now).encode()+b'.'+raw,hashlib.sha256).hexdigest()
        return raw,f't={now},v1={sig}'
    def test_signature_raw_bytes_timestamp_and_livemode(self):
        event={'id':'evt_example','type':'checkout.session.completed','livemode':True,'data':{'object':{'id':'cs_example','client_reference_id':'order-one','payment_status':'paid','amount_total':14900,'currency':'usd'}}}
        raw,header=self.signed(event)
        self.assertEqual(verify_stripe(raw,header,'synthetic-secret',now=1000)['order_id'],'order-one')
        for body,h,secret,now in [(raw+b' ',header,'synthetic-secret',1000),(raw,header,'',1000),(raw,header,'synthetic-secret',1401)]:
            with self.assertRaises(ValueError):verify_stripe(body,h,secret,now=now)
        raw,header=self.signed(dict(event,livemode=False))
        with self.assertRaises(ValueError):verify_stripe(raw,header,'synthetic-secret',now=1000)
    def test_unpaid_checkout_never_counts_as_cash(self):
        event={'id':'evt_example','type':'checkout.session.completed','livemode':True,'data':{'object':{'id':'cs_example','client_reference_id':'order-one','payment_status':'unpaid','amount_total':14900,'currency':'usd'}}}
        raw,header=self.signed(event)
        with self.assertRaises(ValueError):verify_stripe(raw,header,'synthetic-secret',now=1000)


if __name__=='__main__':unittest.main()
