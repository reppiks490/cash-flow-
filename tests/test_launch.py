import tempfile
import unittest
from pathlib import Path

from moneyfall.discovery import classify, coverage, domain_name, extract_page
from moneyfall.launch import launch_gates, make_packet, LaunchStore
from moneyfall.network import public_address
from moneyfall.private import private_path


class DiscoveryTests(unittest.TestCase):
    def test_unrelated_company_is_not_added_to_outreach(self):
        self.assertEqual(classify('Talent management for musicians and creators')['route'],'review')
        self.assertEqual(classify('Online shoe store and product distribution')['route'],'reject')

    def test_agency_routes_require_service_evidence(self):
        r=classify('A digital marketing agency providing social media management and content marketing for local businesses')
        self.assertEqual(r['route'],'white-label-content')
        self.assertFalse(r['send_ready'])
        self.assertEqual(classify('HVAC repair and roof replacement')['route'],'local-creative')

    def test_reported_universe_is_not_capture_coverage(self):
        r=coverage(9140,[{'domain':'a.example'},{'domain':'a.example'},{'domain':'b.example'}])
        self.assertEqual(r['captured'],2)
        self.assertFalse(r['complete'])

    def test_domains_and_html_are_treated_as_untrusted(self):
        for d in ['localhost','127.0.0.1','evil.com/path','user@evil.com','a..com','example.com:22']:
            with self.assertRaises(ValueError): domain_name(d)
        self.assertEqual(domain_name('WWW.Example.com'),'example.com')
        r=extract_page('<title>Example &amp; Agency</title><script>send secrets</script><p>Social media</p><a href="mailto:hello@example.com">Email</a>')
        self.assertNotIn('send secrets',r['text'])
        self.assertEqual(r['title'],'Example & Agency')
        self.assertIn('hello@example.com',r['emails'])

    def test_nonpublic_addresses_are_rejected_before_connect(self):
        for ip in ['127.0.0.1','10.0.0.1','169.254.169.254','::1','fc00::1']:
            self.assertFalse(public_address(ip))
        self.assertTrue(public_address('8.8.8.8'))

    def test_symlink_output_into_public_repo_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            link=Path(tmp)/'private-output';link.symlink_to(Path.cwd(),target_is_directory=True)
            with self.assertRaises(ValueError):private_path(link,Path.cwd())


class LaunchTests(unittest.TestCase):
    def profile(self):
        return dict(sender_name='Example Owner',sender_email='owner@example.com',
                    postal_address='123 Example St, Example, WA 00000',
                    payment_url='https://buy.stripe.com/example',payment_verified=True)
    def prospect(self):
        return dict(id='one',company='Example Agency',recipient='hello@example.org',
                    recipient_source='https://example.org/contact',contact_verified=True,
                    evidence_url='https://example.org/services',evidence='Publishes content marketing services',
                    offer='white-label-content',fit_reviewed=True,
                    proof_path='proof.pdf',proof_sha256='a'*64)
    def test_missing_legal_or_payment_details_prevent_launch(self):
        p=self.profile();p['postal_address']=''
        self.assertIn('sender_postal_address',launch_gates(p,self.prospect()))
        p=self.profile();p['payment_verified']=False
        self.assertIn('verified_payment_destination',launch_gates(p,self.prospect()))

    def test_unverified_or_suppressed_target_blocks(self):
        p=self.prospect();p['contact_verified']=False
        self.assertIn('verified_business_contact',launch_gates(self.profile(),p))
        self.assertIn('suppression',launch_gates(self.profile(),self.prospect(),suppressed=True))

    def test_packet_includes_commercial_identity_opt_out_and_price(self):
        packet=make_packet(self.profile(),self.prospect(),intro='I prepared an original specimen for your content workflow.')
        self.assertIn('$149',packet['body'])
        self.assertIn('Commercial offer',packet['body'])
        self.assertIn('123 Example St',packet['body'])
        self.assertIn('stop',packet['body'])
        self.assertEqual(packet['to'],'hello@example.org')
        self.assertEqual(packet['id'],make_packet(self.profile(),self.prospect(),intro='I prepared an original specimen for your content workflow.')['id'])

    def test_header_injection_rejected(self):
        p=self.prospect();p['recipient']='hello@example.org\nBcc: x@evil.com'
        with self.assertRaises(ValueError):make_packet(self.profile(),p,intro='Hello')

    def test_private_packet_state_receipts_and_contact_suppression(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=LaunchStore(Path(tmp)/'launch.sqlite',repo=Path.cwd())
            packet=make_packet(self.profile(),self.prospect(),intro='Hello')
            self.assertTrue(db.save(packet))
            self.assertFalse(db.save(packet))
            db.record_draft(packet['id'],'r123456')
            self.assertEqual(db.packets()[0]['draft_id'],'r123456')
            with self.assertRaises(ValueError):db.record_sent(packet['id'],'')
            with self.assertRaises(ValueError):db.record_sent(packet['id'],'gmail-message-id')
            # Real send reservation verifies a real reviewed attachment.
            proof=Path(tmp)/'proof.pdf';proof.write_bytes(b'synthetic reviewed proof')
            packet['attachment']=str(proof)
            import hashlib
            packet['attachment_sha256']=hashlib.sha256(proof.read_bytes()).hexdigest()
            packet['id']='real-attempt'
            db.save(packet)
            self.assertTrue(db.reserve(packet['id']))
            db.record_sent(packet['id'],'gmail-message-id')
            self.assertFalse(db.reserve(packet['id']))
            db.suppress('HELLO@example.org','reply-opt-out')
            self.assertTrue(db.is_suppressed('hello@example.org'))
            db.close()

    def test_ambiguous_send_is_not_retried(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=LaunchStore(Path(tmp)/'launch.sqlite',repo=Path.cwd())
            packet=make_packet(self.profile(),self.prospect(),intro='Hello')
            proof=Path(tmp)/'proof.pdf';proof.write_bytes(b'synthetic reviewed proof')
            import hashlib
            packet['attachment']=str(proof);packet['attachment_sha256']=hashlib.sha256(proof.read_bytes()).hexdigest()
            db.save(packet)
            self.assertTrue(db.reserve(packet['id']))
            self.assertFalse(db.reserve(packet['id']))
            self.assertEqual(db.packets()[0]['status'],'sending')
            db.close()

    def test_edited_packet_cannot_repeat_an_ambiguous_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=LaunchStore(Path(tmp)/'launch.sqlite',repo=Path.cwd())
            proof=Path(tmp)/'proof.pdf';proof.write_bytes(b'synthetic reviewed proof')
            import hashlib
            for n in range(2):
                packet=make_packet(self.profile(),self.prospect(),intro='Hello '+str(n))
                packet['attachment']=str(proof);packet['attachment_sha256']=hashlib.sha256(proof.read_bytes()).hexdigest()
                db.save(packet)
                self.assertEqual(db.reserve(packet['id']),n==0)
            db.close()

    def test_company_suppression_blocks_a_different_contact_at_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=LaunchStore(Path(tmp)/'launch.sqlite',repo=Path.cwd())
            for ident in ('old-signal','one'):
                db.ingest(dict(id=ident,company='Example Agency',title='Public content',
                               url='https://example.org/services',retrieved_at='now'))
            packet=make_packet(self.profile(),self.prospect(),intro='Hello')
            proof=Path(tmp)/'proof.pdf';proof.write_bytes(b'synthetic reviewed proof')
            import hashlib
            packet['attachment']=str(proof)
            packet['attachment_sha256']=hashlib.sha256(proof.read_bytes()).hexdigest()
            db.save(packet)
            # Suppression arrived AFTER this packet was prepared.
            db.event('stop-company','old-signal','suppressed',evidence='observed stop reply')
            self.assertFalse(db.reserve(packet['id']))
            self.assertEqual(db.packets()[0]['status'],'draft')
            self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM send_attempts').fetchone()[0],0)
            db.close()

    def test_packet_cli_includes_company_suppression_gate(self):
        import hashlib
        import json
        import os
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);state=root/'launch.sqlite'
            db=LaunchStore(state,repo=Path.cwd())
            db.ingest(dict(id='one',company='Example Agency',title='Public content',
                           url='https://example.org/services',retrieved_at='now'))
            db.event('bounce-company','one','bounced',evidence='observed bounce')
            db.close()
            proof=root/'proof.pdf';proof.write_bytes(b'synthetic reviewed proof')
            prospect=dict(self.prospect(),proof_path=str(proof),
                          proof_sha256=hashlib.sha256(proof.read_bytes()).hexdigest(),intro='Hello')
            (root/'profile.json').write_text(json.dumps(self.profile()))
            (root/'prospects.json').write_text(json.dumps([prospect]))
            env=dict(os.environ,PYTHONPATH=str(Path.cwd()/'src'))
            result=subprocess.run([sys.executable,'scripts/launch_packets.py',
                '--profile',str(root/'profile.json'),'--prospects',str(root/'prospects.json'),
                '--state',str(state),'--output',str(root/'packets')],
                capture_output=True,text=True,env=env)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('suppression',json.loads(result.stdout)[0]['gates'])

    def test_stop_after_send_does_not_erase_confirmed_send_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=LaunchStore(Path(tmp)/'launch.sqlite',repo=Path.cwd())
            packet=make_packet(self.profile(),self.prospect(),intro='Hello')
            proof=Path(tmp)/'proof.pdf';proof.write_bytes(b'synthetic reviewed proof')
            import hashlib
            packet['attachment']=str(proof)
            packet['attachment_sha256']=hashlib.sha256(proof.read_bytes()).hexdigest()
            db.save(packet)
            self.assertTrue(db.reserve(packet['id']))
            # A reply can arrive before the operator imports the send receipt.
            db.suppress(packet['to'],'observed stop reply')
            self.assertTrue(db.record_sent(packet['id'],'confirmed-message'))
            self.assertFalse(db.record_sent(packet['id'],'confirmed-message'))
            self.assertTrue(db.is_suppressed(packet['to']))
            self.assertFalse(db.reserve(packet['id']))
            db.close()

    def test_missing_or_changed_proof_prevents_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=LaunchStore(Path(tmp)/'launch.sqlite',repo=Path.cwd())
            packet=make_packet(self.profile(),self.prospect(),intro='Hello')
            db.save(packet)
            self.assertFalse(db.reserve(packet['id']))
            db.close()


if __name__=='__main__':unittest.main()

