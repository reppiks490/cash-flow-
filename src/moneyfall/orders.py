"""Accepted scope -> verified cash -> approved assets -> checked deliverables."""
import hashlib
import hmac
import json
import re
import time
from datetime import datetime,timezone,timedelta
from pathlib import Path
from .store import Store


def verify_stripe(raw,signature,secret,*,now=None,allow_test=False):
    if not isinstance(raw,bytes) or len(raw)>1_000_000 or not isinstance(secret,str) or not secret:
        raise ValueError('Raw bounded webhook body and private endpoint secret required')
    parts={}
    for pair in signature.split(','):
        key,sep,value=pair.partition('=')
        if sep:parts.setdefault(key.strip(),[]).append(value.strip())
    try:timestamp=int(parts['t'][0])
    except (KeyError,ValueError,IndexError):raise ValueError('Missing webhook timestamp')
    if abs((time.time() if now is None else now)-timestamp)>300:raise ValueError('Expired webhook signature')
    digest=hmac.new(secret.encode(),str(timestamp).encode()+b'.'+raw,hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(digest,s) for s in parts.get('v1',[])):raise ValueError('Invalid webhook signature')
    event=json.loads(raw)
    if event.get('livemode') is not True and not allow_test:raise ValueError('Test events cannot count as live revenue')
    if event.get('type') not in ('checkout.session.completed','checkout.session.async_payment_succeeded'):
        raise ValueError('Unsupported checkout event')
    session=event.get('data',{}).get('object',{})
    if session.get('payment_status')!='paid' or session.get('currency')!='usd':raise ValueError('Checkout has no confirmed USD payment')
    amount=session.get('amount_total')
    if isinstance(amount,bool) or not isinstance(amount,int) or amount<=0:raise ValueError('Invalid payment amount')
    for field in ('id','client_reference_id'):
        if not isinstance(session.get(field),str) or not session[field]:raise ValueError('Checkout lacks reconciliation IDs')
    return dict(order_id=session['client_reference_id'],receipt='stripe:'+session['id'],amount_cents=amount,event_id=event['id'])


class Orders(Store):
    def __init__(self,path,*,repo):
        super().__init__(path,repo=repo)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS orders (
            id TEXT PRIMARY KEY, signal_id TEXT NOT NULL REFERENCES signals(id),
            scope TEXT NOT NULL, price INTEGER NOT NULL, paid_receipt TEXT UNIQUE,
            assets_reference TEXT, delivered_reference TEXT, created_at TEXT NOT NULL,
            due_at TEXT)''')
        self.conn.commit()
        columns={row[1] for row in self.conn.execute('PRAGMA table_info(orders)')}
        for name,kind,default in [('attribution','TEXT',"'{}'"),('refunded','INTEGER','0'),('produced_reference','TEXT','NULL'),('delivery_receipt','TEXT','NULL')]:
            if name not in columns:self.conn.execute(f'ALTER TABLE orders ADD COLUMN {name} {kind} DEFAULT {default}')
        self.conn.commit()
    def create_order(self,ident,signal_id,*,scope,price_cents):
        if not isinstance(ident,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,200}',ident):raise ValueError('Invalid order ID')
        if not isinstance(scope,str) or not scope.strip():raise ValueError('Accepted scope is required')
        if isinstance(price_cents,bool) or not isinstance(price_cents,int) or price_cents<=0:raise ValueError('Price must be positive integer cents')
        if not self.conn.execute('SELECT 1 FROM signals WHERE id=?',(signal_id,)).fetchone():raise ValueError('Unknown signal')
        signal=json.loads(self.conn.execute('SELECT payload FROM signals WHERE id=?',(signal_id,)).fetchone()[0])
        attribution=dict(signal.get('attribution',{}),order_id=ident)
        with self.conn:self.conn.execute('INSERT INTO orders(id,signal_id,scope,price,created_at,attribution) VALUES(?,?,?,?,?,?)',(ident,signal_id,scope.strip(),price_cents,datetime.now(timezone.utc).isoformat(),json.dumps(attribution)))
    def get_order(self,ident):
        cur=self.conn.execute('SELECT * FROM orders WHERE id=?',(ident,));row=cur.fetchone()
        if not row:raise ValueError('Unknown order')
        return dict(zip([c[0] for c in cur.description],row))
    def payment(self,ident,receipt,amount_cents):
        if not isinstance(receipt,str) or not receipt.strip():raise ValueError('Verified receipt reference required')
        receipt=receipt.strip()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            order=self.get_order(ident)
            if isinstance(amount_cents,bool) or not isinstance(amount_cents,int) or amount_cents!=order['price']:raise ValueError('Payment amount differs from accepted scope')
            if order['paid_receipt']:
                if order['paid_receipt']!=receipt:raise ValueError('Order already paid with another receipt')
                self.conn.rollback();return False
            if self.conn.execute("SELECT 1 FROM events WHERE kind='payment' AND evidence=?",(receipt,)).fetchone():raise ValueError('Payment receipt already attributed')
            self.conn.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?)',('order-payment:'+receipt,order['signal_id'],'payment',amount_cents,receipt,datetime.now(timezone.utc).isoformat(),order['attribution']))
            self.conn.execute('UPDATE orders SET paid_receipt=? WHERE id=?',(receipt,ident))
            self.start_deadline(ident)
            self.conn.commit();return True
        except Exception:self.conn.rollback();raise
    def assets(self,ident,*,licensed,reference):
        self.get_order(ident)
        if licensed is not True or not isinstance(reference,str) or not reference.strip():raise ValueError('Approved brief and commercial asset permissions required')
        with self.conn:
            self.conn.execute('UPDATE orders SET assets_reference=? WHERE id=?',(reference.strip(),ident))
            self.start_deadline(ident)
    def start_deadline(self,ident):
        order=self.get_order(ident)
        if order['paid_receipt'] and order['assets_reference'] and not order['due_at']:
            self.conn.execute('UPDATE orders SET due_at=? WHERE id=?',((datetime.now(timezone.utc)+timedelta(hours=48)).isoformat(),ident))
    def ready(self,ident):
        order=self.get_order(ident)
        ambiguous=self.conn.execute("SELECT 1 FROM events WHERE signal_id=? AND kind='refund' AND id NOT LIKE 'order-refund:%'",(order['signal_id'],)).fetchone()
        return bool(order['paid_receipt'] and order['assets_reference'] and order['refunded']==0 and not ambiguous and not order['delivery_receipt'])
    def refund(self,ident,receipt,amount_cents):
        if not isinstance(receipt,str) or not receipt.strip():raise ValueError('Verified refund receipt required')
        receipt=receipt.strip()
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            order=self.get_order(ident)
            existing=self.conn.execute("SELECT amount,attribution FROM events WHERE kind='refund' AND evidence=?",(receipt,)).fetchone()
            if existing:
                if existing[0]!=amount_cents or json.loads(existing[1]).get('order_id')!=ident:raise ValueError('Conflicting refund receipt')
                self.conn.rollback();return False
            if not order['paid_receipt'] or isinstance(amount_cents,bool) or not isinstance(amount_cents,int) or not 0<amount_cents<=order['price']-order['refunded']:raise ValueError('Refund exceeds this order balance')
            self.conn.execute('INSERT INTO events VALUES(?,?,?,?,?,?,?)',('order-refund:'+ident+':'+receipt,order['signal_id'],'refund',amount_cents,receipt,datetime.now(timezone.utc).isoformat(),order['attribution']))
            self.conn.execute('UPDATE orders SET refunded=refunded+? WHERE id=?',(amount_cents,ident))
            self.conn.commit();return True
        except Exception:self.conn.rollback();raise
    def fulfill(self,ident,folder):
        if not self.ready(ident):raise ValueError('Order is not ready for fulfillment')
        folder=Path(folder).resolve()
        path=folder/'manifest.json'
        if not path.is_file():raise ValueError('Missing fulfillment manifest')
        manifest=json.loads(path.read_text())
        if manifest.get('order_id')!=ident or manifest.get('scope_sha256')!=hashlib.sha256(self.get_order(ident)['scope'].encode()).hexdigest():raise ValueError('Kit is not bound to this accepted order')
        required={'proof.pdf','captions.md','motion-preview.mp4'}|{f'card-{n:03}.{ext}' for n in (1,2,3) for ext in ('png','svg')}
        if manifest.get('specimen') is not False:raise ValueError('Specimen cannot be delivered as commissioned work')
        if not required<=manifest.get('files',{}).keys():raise ValueError('Incomplete delivery kit')
        for name in required:
            file=folder/name
            if not file.is_file() or not file.resolve().is_relative_to(folder) or hashlib.sha256(file.read_bytes()).hexdigest()!=manifest['files'][name]:raise ValueError('Delivery file missing or changed')
            data=file.read_bytes()
            if name.endswith('.png') and (not data.startswith(b'\x89PNG\r\n\x1a\n') or len(data)<24):raise ValueError('Invalid portrait image')
            if name.endswith('.pdf') and (not data.startswith(b'%PDF-') or not data.rstrip().endswith(b'%%EOF')):raise ValueError('Invalid proof PDF')
            if name.endswith('.mp4') and (len(data)<12 or data[4:8]!=b'ftyp'):raise ValueError('Invalid motion video')
            if name.endswith('.svg'):
                from xml.etree import ElementTree
                svg=ElementTree.fromstring(data)
                if svg.tag.split('}')[-1]!='svg' or any(n.tag.split('}')[-1] in ('script','foreignObject') for n in svg.iter()):raise ValueError('Invalid or active SVG')
        reference=hashlib.sha256(path.read_bytes()).hexdigest()
        with self.conn:self.conn.execute('UPDATE orders SET produced_reference=? WHERE id=?',(reference,ident))
        return reference
    def delivered(self,ident,receipt):
        order=self.get_order(ident)
        if not order['produced_reference'] or not isinstance(receipt,str) or not receipt.strip():raise ValueError('Validated production and actual delivery receipt required')
        if order['delivery_receipt']:
            if order['delivery_receipt']!=receipt.strip():raise ValueError('Conflicting delivery receipt')
            return False
        with self.conn:self.conn.execute('UPDATE orders SET delivery_receipt=?,delivered_reference=produced_reference WHERE id=?',(receipt.strip(),ident))
        return True
