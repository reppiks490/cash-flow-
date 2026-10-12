import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from moneyfall.offers import brief


class OfferTests(unittest.TestCase):
    def test_brief_marks_unverified_hypotheses_and_escapes_injected_markup(self):
        text = brief(dict(id='one',company='<script>',title='Video editor',
                          url='https://example.org/jobs/1'), 'content-repurpose')
        self.assertIn('Unverified',text)
        self.assertIn('149',text)
        self.assertNotIn('<script>',text)
        self.assertIn('https://example.org/jobs/1',text)


class CLITests(unittest.TestCase):
    def test_boolean_qualification_evidence_is_rejected(self):
        from moneyfall.store import Store
        from moneyfall.scoring import DIMENSIONS
        with tempfile.TemporaryDirectory() as folder:
            state=Path(folder)/'state.sqlite'
            db=Store(state,repo=Path.cwd())
            db.ingest(dict(id='one',company='Example',title='Editor',url='https://example.org',retrieved_at='now'))
            db.close()
            evidence=Path(folder)/'evidence.json'
            evidence.write_text(json.dumps(dict(dimensions=dict.fromkeys(DIMENSIONS,1),evidence=dict.fromkeys(DIMENSIONS,True))))
            r=subprocess.run([sys.executable,'-m','moneyfall','--state',str(state),'qualify','one',str(evidence)],capture_output=True,text=True)
            self.assertNotEqual(r.returncode,0)

    def test_deterministic_demo_has_no_live_revenue(self):
        result = subprocess.run([sys.executable,'-m','moneyfall','demo'],
                                capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertEqual(data['mode'],'synthetic')
        self.assertEqual(data['metrics']['net_revenue_cents'],10000)
        self.assertEqual(data['live_revenue_cents'],0)

    def test_rank_hypotheses_and_cli_refuses_repo_state(self):
        r=subprocess.run([sys.executable,'-m','moneyfall','rank'],capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads(r.stdout)['basis'],'scenario assumptions, not observed conversion rates')
        r=subprocess.run([sys.executable,'-m','moneyfall','--state',str(Path.cwd()/'bad.sqlite'),'metrics'],capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0)
        self.assertIn('outside',r.stderr)


if __name__=='__main__':
    unittest.main()
