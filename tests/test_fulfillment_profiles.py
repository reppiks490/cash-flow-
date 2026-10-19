import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from moneyfall.fulfillment_profiles import record_document_fulfillment, validate_bundle


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


class FakeOrders:
    def __init__(self, scope='scope', ready=True):
        self.scope = scope
        self._ready = ready
        self.writes = []

        class Conn:
            def __init__(self, outer):
                self.outer = outer
            def __enter__(self):
                return self
            def __exit__(self, exc_type, exc, tb):
                return False
            def execute(self, sql, params):
                self.outer.writes.append((sql, params))

        self.conn = Conn(self)

    def ready(self, ident):
        return self._ready

    def get_order(self, ident):
        return {'scope': self.scope}


class DocumentOrderHandoffTests(unittest.TestCase):
    def test_record_document_fulfillment_requires_ready_order_and_updates_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            payload = b'%PDF-1.4\nbody\n%%EOF\n'
            (folder/'deliverable.pdf').write_bytes(payload)
            manifest = {
                'order_id': 'order-123',
                'scope_sha256': hashlib.sha256(b'scope').hexdigest(),
                'profile': 'document-v1',
                'specimen': False,
                'files': {'deliverable.pdf': hashlib.sha256(payload).hexdigest()},
            }
            (folder/'manifest.json').write_text(json.dumps(manifest))
            orders = FakeOrders()
            ref = record_document_fulfillment(orders, 'order-123', folder)
            self.assertTrue(ref)
            self.assertEqual(orders.writes[0][1], (ref, 'order-123'))
            with self.assertRaisesRegex(ValueError, 'not ready'):
                record_document_fulfillment(FakeOrders(ready=False), 'order-123', folder)


if __name__ == '__main__':
    unittest.main()
