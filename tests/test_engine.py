import math
import tempfile
import unittest
from pathlib import Path

from moneyfall.scoring import opportunity_score, promote, readiness
from moneyfall.sources import normalize, source_url
from moneyfall.store import Store


class ScoringTests(unittest.TestCase):
    def scenario(self, **overrides):
        return dict(probability=.4, days=3, margin=.8, urgency=.8,
                    reachability=.7, automation=.8, scale=.6, defensibility=.4,
                    upfront_cents=0, **overrides)

    def test_unknown_dimension_blocks_prospect(self):
        r = readiness(dict(budget=.8, deficiency=None, value=.8,
                           reachability=.7, demonstrability=.8, speed=.8))
        self.assertEqual(r['score'], 0)
        self.assertEqual(r['missing'], ['deficiency'])

    def test_paid_or_invalid_opportunities_rejected(self):
        s = self.scenario()
        self.assertEqual(opportunity_score(dict(s, upfront_cents=1)), 0)
        for bad in (float('nan'), float('inf'), -.1, 1.1):
            with self.assertRaises(ValueError):
                opportunity_score(dict(s, probability=bad))
        with self.assertRaises(ValueError):
            opportunity_score(dict(s, days=0))

    def test_promotion_requires_observed_cash_and_material_advantage(self):
        self.assertFalse(promote(10, 100, paid_conversions=0))
        self.assertFalse(promote(10, 10.5, paid_conversions=3))
        self.assertTrue(promote(10, 12, paid_conversions=3))
        for n in (3.5, float('inf'), True, -1):
            with self.assertRaises(ValueError):
                promote(10,12,paid_conversions=n)

    def test_readiness_product(self):
        self.assertAlmostEqual(readiness(dict.fromkeys(
            ['budget','deficiency','value','reachability','demonstrability','speed'], .5))['score'], 1.5625)


class SourceTests(unittest.TestCase):
    def test_source_token_cannot_inject_url(self):
        with self.assertRaises(ValueError):
            source_url('greenhouse', '../secret?x=1')
        with self.assertRaises(ValueError):
            source_url('unknown', 'example')

    def test_greenhouse_updated_time_not_claimed_as_posting_time(self):
        jobs = normalize('greenhouse', 'example', {'jobs':[
            {'id':1,'title':'Growth marketer','absolute_url':'https://example.org/jobs/1',
             'updated_at':'2026-10-01T12:00:00Z'},
            {'id':2,'title':'Engineer','absolute_url':'https://example.org/jobs/2'}]},
            '2026-10-12T00:00:00Z')
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['source_time_kind'], 'updated')
        self.assertEqual(jobs[0]['retrieved_at'], '2026-10-12T00:00:00Z')

    def test_lever_and_invalid_payload(self):
        jobs = normalize('lever','example',[{'id':'one','text':'Video editor',
            'hostedUrl':'https://jobs.lever.co/example/one','createdAt':0}],
            '2026-10-12T00:00:00Z')
        self.assertEqual(jobs[0]['source_time_kind'], 'created')
        self.assertEqual(jobs[0]['source_time'], '1970-01-01T00:00:00+00:00')
        with self.assertRaises(ValueError):
            normalize('greenhouse','example',{},'now')

    def test_sales_hiring_is_discoverable(self):
        jobs=normalize('greenhouse','example',{'jobs':[{'id':1,'title':'Sales Development Representative','absolute_url':'https://example.org/job'}]},'now')
        self.assertEqual(len(jobs),1)


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Store(Path(self.tmp.name)/'state.sqlite', repo=Path.cwd())
    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()
    def signal(self):
        return dict(id='gh:one', company='Example', title='Growth',
                    url='https://example.org', retrieved_at='2026-10-12T00:00:00Z')
    def test_duplicate_signals_keep_first_seen(self):
        self.assertTrue(self.db.ingest(self.signal()))
        self.assertFalse(self.db.ingest(dict(self.signal(), title='Growth director')))
        self.assertEqual(len(self.db.signals()),1)
        self.assertEqual(self.db.signals()[0]['title'],'Growth director')
    def test_state_inside_repo_rejected(self):
        with self.assertRaises(ValueError):
            Store(Path.cwd()/'private.sqlite',repo=Path.cwd())
    def test_money_events_idempotent_and_refunds_reduce_cash(self):
        self.db.ingest(self.signal())
        self.assertTrue(self.db.event('paid-1','gh:one','payment',14900,'receipt-1'))
        self.assertFalse(self.db.event('paid-1','gh:one','payment',14900,'receipt-1'))
        self.db.event('refund-1','gh:one','refund',4900,'refund-receipt')
        self.db.event('cost-1','gh:one','cost',1000,'invoice-1')
        report = self.db.metrics()
        self.assertEqual(report['net_revenue_cents'],10000)
        self.assertEqual(report['gross_profit_cents'],9000)
        self.assertEqual(report['paid_prospects'],1)
    def test_unknown_signal_or_unverified_money_rejected(self):
        with self.assertRaises(ValueError):
            self.db.event('p','missing','payment',100,'receipt')
        self.db.ingest(self.signal())
        with self.assertRaises(ValueError):
            self.db.event('p','gh:one','payment',100,'')
    def test_suppression_and_permission(self):
        self.db.ingest(self.signal())
        self.db.event('s','gh:one','suppressed',0,'opt-out')
        self.assertTrue(self.db.suppressed('gh:one'))
        self.assertEqual(self.db.path.stat().st_mode & 0o777,0o600)

    def test_multiple_jobs_at_one_company_are_one_prospect_and_suppression(self):
        self.db.ingest(self.signal())
        self.db.ingest(dict(self.signal(),id='gh:two'))
        self.assertEqual(self.db.metrics()['prospects'],1)
        self.db.event('s','gh:one','suppressed',0,'opt-out')
        self.assertTrue(self.db.suppressed('gh:two'))

    def test_payment_receipt_cannot_be_counted_twice(self):
        self.db.ingest(self.signal())
        self.db.event('p','gh:one','payment',100,'receipt')
        with self.assertRaises(ValueError):
            self.db.event('other-p','gh:one','payment',100,'receipt')
        with self.assertRaises(ValueError):
            self.db.event('spaced-p','gh:one','payment',100,' receipt ')

    def test_refund_cannot_exceed_collected_cash(self):
        self.db.ingest(self.signal())
        self.db.event('p','gh:one','payment',100,'receipt')
        with self.assertRaises(ValueError):
            self.db.event('r','gh:one','refund',101,'refund-receipt')

    def test_refresh_retains_qualification_unless_claim_changes(self):
        self.db.ingest(dict(self.signal(),dimensions={'budget':.8},qualification_evidence={'budget':'source'}))
        self.db.ingest(self.signal())
        self.assertEqual(self.db.signals()[0]['dimensions'],{'budget':.8})
        self.db.ingest(dict(self.signal(),title='Different role'))
        self.assertNotIn('dimensions',self.db.signals()[0])

    def test_events_keep_original_opportunity_attribution(self):
        self.db.ingest(dict(self.signal(),attribution={'opportunity_id':'incumbent','offer_id':'offer','asset_id':'proof','hypothesis':'test'}))
        self.db.event('p','gh:one','payment',100,'receipt')
        self.db.ingest(dict(self.signal(),attribution={'opportunity_id':'challenger'}))
        self.assertEqual(self.db.metrics(opportunity_id='incumbent')['net_revenue_cents'],100)
        self.assertEqual(self.db.metrics(opportunity_id='challenger')['net_revenue_cents'],0)


if __name__ == '__main__':
    unittest.main()
