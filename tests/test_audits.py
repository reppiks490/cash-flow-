import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from moneyfall.audits import validate_audit, render_html, render_markdown, write_audit


ROOT=Path(__file__).resolve().parents[1]


class AuditTests(unittest.TestCase):
    def payload(self):
        return json.loads((ROOT/'config/examples/research_audit.json').read_text())

    def test_validated_report_keeps_source_linkage_and_does_not_mutate_input(self):
        payload=self.payload();before=json.dumps(payload,sort_keys=True)
        report=validate_audit(payload)
        self.assertEqual(report['findings'][0]['source_id'],'services')
        self.assertEqual(json.dumps(payload,sort_keys=True),before)

    def test_quote_must_exist_in_supplied_evidence(self):
        payload=self.payload();payload['findings'][0]['evidence_quote']='Invented customer claim'
        with self.assertRaises(ValueError):validate_audit(payload)

    def test_unknown_source_cannot_support_a_finding(self):
        payload=self.payload();payload['findings'][0]['source_id']='unknown'
        with self.assertRaises(ValueError):validate_audit(payload)

    def test_unreviewed_real_report_is_not_exported(self):
        payload=self.payload();payload.update(mode='review',reviewed=False)
        with self.assertRaises(ValueError):validate_audit(payload)

    def test_source_links_are_public_https_without_credentials_or_control_chars(self):
        for url in ('javascript:alert(1)','https://localhost/','https://127.0.0.1/',
                    'https://user:password@example.org/','https://example.org:8080/',
                    'https://example.org/\nsecret'):
            with self.subTest(url=url):
                payload=self.payload();payload['sources'][0]['url']=url
                with self.assertRaises(ValueError):validate_audit(payload)

    def test_observation_timestamp_requires_timezone(self):
        payload=self.payload();payload['sources'][0]['observed_at']='2026-10-12T01:00:00'
        with self.assertRaises(ValueError):validate_audit(payload)

    def test_duplicate_source_ids_are_rejected(self):
        payload=self.payload();payload['sources'][1]['id']='services'
        with self.assertRaises(ValueError):validate_audit(payload)

    def test_required_content_and_size_bounds(self):
        for field,value in [('sources',[]),('findings',[]),('findings',[self.payload()['findings'][0]]*9),
                            ('limitations',['x']*9),('schema_version',True),('mode','paid')]:
            with self.subTest(field=field):
                payload=self.payload();payload[field]=value
                with self.assertRaises(ValueError):validate_audit(payload)

    def test_html_and_markdown_escape_untrusted_text(self):
        payload=self.payload();payload['company']='<script>alert(1)</script>'
        payload['findings'][0]['recommended_action']='<img src=x onerror=alert(2)>'
        report=validate_audit(payload)
        markup=render_html(report)
        self.assertNotIn('<script>',markup);self.assertNotIn('<img src=x',markup)
        self.assertIn('&lt;script&gt;',markup)
        self.assertNotIn('<script>',render_markdown(report))

    def test_mode_and_unknown_results_remain_explicit_in_both_formats(self):
        for mode in ('specimen','review'):
            report=validate_audit(dict(self.payload(),mode=mode))
            for text in (render_html(report),render_markdown(report)):
                self.assertIn(mode.upper(),text)
                self.assertIn('not measured',text)

    def test_private_export_has_hashes_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'audit'
            summary=write_audit(self.payload(),output,ROOT)
            manifest=json.loads((output/'manifest.json').read_text())
            self.assertEqual(summary['mode'],'specimen')
            self.assertTrue(manifest['specimen'])
            original=json.dumps(self.payload(),sort_keys=True,allow_nan=False).encode()
            self.assertEqual(manifest['input_sha256'],hashlib.sha256(original).hexdigest())
            for name,digest in manifest['files'].items():
                self.assertEqual(hashlib.sha256((output/name).read_bytes()).hexdigest(),digest)
                if os.name=='posix':self.assertEqual((output/name).stat().st_mode & 0o777,0o600)
            before=(output/'audit.html').read_bytes()
            with self.assertRaises(FileExistsError):write_audit(self.payload(),output,ROOT)
            self.assertEqual((output/'audit.html').read_bytes(),before)

    def test_symlink_back_into_checkout_is_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            link=Path(tmp)/'redirect';link.symlink_to(ROOT,target_is_directory=True)
            with self.assertRaises(ValueError):write_audit(self.payload(),link/'audit',ROOT)

    def test_invalid_payload_leaves_no_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'audit';payload=self.payload();payload['findings'][0]['source_id']='unknown'
            with self.assertRaises(ValueError):write_audit(payload,output,ROOT)
            self.assertFalse(output.exists())

    @unittest.skipUnless(importlib.util.find_spec('reportlab'),'Optional PDF dependency absent')
    def test_pdf_rejects_unsupported_glyphs_without_partial_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'audit';payload=self.payload();payload['company']='日本語：東京の株式会社'
            with self.assertRaisesRegex(ValueError,'glyph'):
                write_audit(payload,output,ROOT,pdf=True)
            self.assertFalse(output.exists())

    @unittest.skipUnless(importlib.util.find_spec('reportlab'),'Optional PDF dependency absent')
    def test_exporter_failure_removes_only_new_partial_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'audit';sibling=Path(tmp)/'keep';sibling.write_text('preserve')
            with patch('moneyfall.audits._write_pdf',side_effect=RuntimeError('export failed')):
                with self.assertRaises(RuntimeError):write_audit(self.payload(),output,ROOT,pdf=True)
            self.assertFalse(output.exists());self.assertEqual(sibling.read_text(),'preserve')

    def test_source_bytes_must_match_the_supplied_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'audit'
            with self.assertRaises(ValueError):
                write_audit(self.payload(),output,ROOT,source_bytes=b'{}')
            self.assertFalse(output.exists())

    def test_missing_optional_pdf_dependency_fails_before_output(self):
        actual_import=__import__
        def without_pdf(name,*args,**kwargs):
            if name.startswith('reportlab'):raise ImportError('optional dependency unavailable')
            return actual_import(name,*args,**kwargs)
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'audit'
            with patch('builtins.__import__',side_effect=without_pdf):
                with self.assertRaisesRegex(ValueError,'optional ReportLab'):
                    write_audit(self.payload(),output,ROOT,pdf=True)
            self.assertFalse(output.exists())

    def test_real_cli_produces_private_files_without_echoing_company(self):
        with tempfile.TemporaryDirectory() as tmp:
            output=Path(tmp)/'audit'
            env=dict(os.environ,PYTHONPATH=str(ROOT/'src'))
            result=subprocess.run([sys.executable,str(ROOT/'scripts/render_audit.py'),
                str(ROOT/'config/examples/research_audit.json'),str(output)],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(result.stdout)['findings'],2)
            self.assertNotIn('Northstar',result.stdout)
            self.assertTrue((output/'audit.html').exists())
            manifest=json.loads((output/'manifest.json').read_text())
            source=(ROOT/'config/examples/research_audit.json').read_bytes()
            self.assertEqual(manifest['input_sha256'],hashlib.sha256(source).hexdigest())
            self.assertEqual(manifest['input_hash_basis'],'exact_source_bytes')


if __name__=='__main__':unittest.main()
