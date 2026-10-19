"""Validation for non-creative MONEYFALL fulfillment bundles."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def validate_bundle(folder, *, order_id: str, scope: str) -> str:
    folder = Path(folder).resolve()
    manifest_path = folder / 'manifest.json'
    if not manifest_path.is_file():
        raise ValueError('Missing fulfillment manifest')
    manifest = json.loads(manifest_path.read_text())
    if manifest.get('order_id') != order_id:
        raise ValueError('Bundle is not bound to this order')
    if manifest.get('scope_sha256') != hashlib.sha256(scope.encode()).hexdigest():
        raise ValueError('Bundle is not bound to this accepted scope')
    if manifest.get('profile') != 'document-v1':
        raise ValueError('Unsupported fulfillment profile')
    if manifest.get('specimen') is not False:
        raise ValueError('Specimen cannot be delivered as commissioned work')
    files = manifest.get('files')
    if not isinstance(files, dict) or 'deliverable.pdf' not in files:
        raise ValueError('Document bundle requires deliverable.pdf')
    file = (folder / 'deliverable.pdf').resolve()
    if not file.is_file() or not file.is_relative_to(folder):
        raise ValueError('Delivery file missing or invalid')
    data = file.read_bytes()
    if hashlib.sha256(data).hexdigest() != files['deliverable.pdf']:
        raise ValueError('Delivery file changed')
    if not data.startswith(b'%PDF-') or not data.rstrip().endswith(b'%%EOF'):
        raise ValueError('Invalid proof PDF')
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()


def record_document_fulfillment(orders, ident: str, folder) -> str:
    if not orders.ready(ident):
        raise ValueError('Order is not ready for document fulfillment')
    order = orders.get_order(ident)
    reference = validate_bundle(folder, order_id=ident, scope=order['scope'])
    with orders.conn:
        orders.conn.execute('UPDATE orders SET produced_reference=? WHERE id=?', (reference, ident))
    return reference
