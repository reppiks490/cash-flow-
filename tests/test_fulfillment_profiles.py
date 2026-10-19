import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from moneyfall.fulfillment_profiles import validate_bundle


class FulfillmentProfileTests(unittest.TestCase):
    def test_document_bundle_accepts_required_pdf_and_manifest_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = b'%PDF-1.4\nbody\n%%EOF\n'
            (folder/'deliverable.pdf').write_bytes(payload)
            manifest = {
                'order_id': 'order-123',
                'scope_sha256': hashlib.sha256(b'permit readiness research pack').hexdigest(),
                'profile': 'document-v1',
                'specimen': False,
                'files': {'deliverable.pdf': hashlib.sha256(payload).hexdigest()},
            }
            (folder/'manifest.json').write_text(json.dumps(manifest))
            ref = validate_bundle(folder, order_id='order-123', scope='permit readiness research pack')
            self.assertEqual(ref, hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest())

    def test_document_bundle_rejects_specimen_or_changed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = b'%PDF-1.4\nbody\n%%EOF\n'
            (folder/'deliverable.pdf').write_bytes(payload)
            manifest = {
                'order_id': 'order-123',
                'scope_sha256': hashlib.sha256(b'scope').hexdigest(),
                'profile': 'document-v1',
                'specimen': True,
                'files': {'deliverable.pdf': hashlib.sha256(payload).hexdigest()},
            }
            (folder/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'Specimen'):
                validate_bundle(folder, order_id='order-123', scope='scope')
            manifest['specimen'] = False
            (folder/'manifest.json').write_text(json.dumps(manifest))
            (folder/'deliverable.pdf').write_bytes(payload+b'x')
            with self.assertRaisesRegex(ValueError, 'changed'):
                validate_bundle(folder, order_id='order-123', scope='scope')


if __name__ == '__main__':
    unittest.main()
