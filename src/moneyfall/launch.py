"""Private launch packets and send reservations; no invented delivery receipts."""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlparse
from .store import Store


def email(value):
    if not isinstance(value,str) or not re.fullmatch(r'[^\s<>@,;]+@[^\s<>@,;]+\.[A-Za-z]{2,}',value):
        raise ValueError('Expected one business email without header delimiters')
    return value.casefold()


def public_https(value):
    if not isinstance(value,str):return False
    p=urlparse(value)
    return p.scheme=='https' and bool(p.hostname) and not p.username and not p.password


def launch_gates(profile,prospect,*,suppressed=False):
    missing=[]
    if not profile.get('sender_name'):missing.append('sender_identity')
    try:email(profile.get('sender_email'))
    except ValueError:missing.append('sender_email')
    if not isinstance(profile.get('postal_address'),str) or not profile['postal_address'].strip():missing.append('sender_postal_address')
    if profile.get('payment_verified') is not True or not public_https(profile.get('payment_url')):missing.append('verified_payment_destination')
    try:email(prospect.get('recipient'))
    except ValueError:missing.append('business_recipient')
    if prospect.get('contact_verified') is not True or not public_https(prospect.get('recipient_source')):missing.append('verified_business_contact')
    if prospect.get('fit_reviewed') is not True or not public_https(prospect.get('evidence_url')) or not isinstance(prospect.get('evidence'),str) or not prospect['evidence'].strip():missing.append('reviewed_offer_fit')
    if not prospect.get('proof_path') or not re.fullmatch(r'[a-f0-9]{64}',prospect.get('proof_sha256','')):missing.append('proof_asset')
    if suppressed:missing.append('suppression')
    return missing


def make_packet(profile,prospect,*,intro):
    recipient=email(prospect.get('recipient'))
    sender=email(profile.get('sender_email'))
    if not isinstance(intro,str) or not intro.strip():raise ValueError('Personalized intro is required')
    company=prospect['company']
    if '\n' in company or '\r' in company:raise ValueError('Company name cannot contain header delimiters')
    subject=f'An original content pilot for {company}'
    address=profile.get('postal_address') or '[REQUIRED: VALID SENDER POSTAL ADDRESS]'
    body=f'''Hi,

{intro.strip()}

I prepared the attached original spec sample. It is a concept, not a client
result or a claim that your current marketing is underperforming.

For $149, I can deliver a white-label content kit: three portrait graphics with
editable SVG files, one 15-second caption-led motion preview, three captions
and CTA options, and one revision. Delivery is within 48 hours of an accepted
brief, payment and approved brand assets. No subscription or ad spend required.
No promised leads or revenue. Filming, voiceover and account management excluded.

Would a one-project pilot be useful for your current content workload?

{profile['sender_name']}
Commercial offer. Reply "stop" to receive no further marketing emails.
{address}
'''
    packet=dict(signal_id=prospect['id'],company=company,to=recipient,from_email=sender,
                subject=subject,body=body,attachment=prospect['proof_path'],
                attachment_sha256=prospect['proof_sha256'],offer_id='white-label-kit-v1',
                opportunity_id='signal-driven-b2b',price_cents=14900,
                gates=launch_gates(profile,prospect),recipient_source=prospect['recipient_source'],
                evidence_url=prospect['evidence_url'])
    packet['id']=hashlib.sha256(json.dumps(packet,sort_keys=True).encode()).hexdigest()
    return packet


class LaunchStore(Store):
    def __init__(self,path,*,repo):
        super().__init__(path,repo=repo)
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS packets (
                id TEXT PRIMARY KEY, recipient TEXT NOT NULL, payload TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'draft', receipt TEXT, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS contact_suppression (
                recipient TEXT PRIMARY KEY, evidence TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS send_attempts (
                id TEXT PRIMARY KEY, packet_id TEXT NOT NULL UNIQUE);
        ''')
        if 'draft_id' not in {r[1] for r in self.conn.execute('PRAGMA table_info(packets)')}:
            self.conn.execute('ALTER TABLE packets ADD COLUMN draft_id TEXT')
            self.conn.commit()
    def record_draft(self,ident,draft_id):
        if not isinstance(draft_id,str) or not draft_id.strip():raise ValueError('Observed provider draft ID required')
        with self.conn:
            row=self.conn.execute('SELECT draft_id FROM packets WHERE id=?',(ident,)).fetchone()
            if row is None:raise ValueError('Unknown packet')
            if row[0] and row[0]!=draft_id:raise ValueError('Conflicting draft receipt')
            self.conn.execute('UPDATE packets SET draft_id=? WHERE id=?',(draft_id,ident))
    def save(self,packet):
        with self.conn:
            cur=self.conn.execute('INSERT OR IGNORE INTO packets(id,recipient,payload,created_at) VALUES (?,?,?,?)',
                                  (packet['id'],email(packet['to']),json.dumps(packet,allow_nan=False),datetime.now(timezone.utc).isoformat()))
        return cur.rowcount==1
    def is_suppressed(self,recipient):
        return bool(self.conn.execute('SELECT 1 FROM contact_suppression WHERE recipient=?',(email(recipient),)).fetchone())
    def suppress(self,recipient,evidence):
        if not isinstance(evidence,str) or not evidence.strip():raise ValueError('Suppression requires observed evidence')
        with self.conn:self.conn.execute('INSERT OR REPLACE INTO contact_suppression VALUES (?,?,?)',(email(recipient),evidence.strip(),datetime.now(timezone.utc).isoformat()))
    def packets(self):
        return [dict(json.loads(p),status=s,receipt=r,draft_id=d) for p,s,r,d in self.conn.execute('SELECT payload,status,receipt,draft_id FROM packets ORDER BY created_at,id')]
    def reserve(self,ident):
        self.conn.execute('BEGIN IMMEDIATE')
        try:
            row=self.conn.execute('SELECT recipient,payload,status FROM packets WHERE id=?',(ident,)).fetchone()
            if not row or row[2]!='draft':self.conn.rollback();return False
            packet=json.loads(row[1])
            if self.is_suppressed(row[0]) or self.suppressed(packet['signal_id']) or packet.get('gates'):
                self.conn.rollback();return False
            proof=Path(packet['attachment'])
            if not proof.is_file() or hashlib.sha256(proof.read_bytes()).hexdigest()!=packet['attachment_sha256']:self.conn.rollback();return False
            attempt=hashlib.sha256(json.dumps([row[0],packet['offer_id'],packet.get('stage','initial')]).encode()).hexdigest()
            new=self.conn.execute('INSERT OR IGNORE INTO send_attempts VALUES (?,?)',(attempt,ident))
            if new.rowcount!=1:self.conn.rollback();return False
            cur=self.conn.execute("UPDATE packets SET status='sending' WHERE id=? AND status='draft'",(ident,))
            self.conn.commit();return cur.rowcount==1
        except Exception:self.conn.rollback();raise
    def record_sent(self,ident,receipt):
        if not isinstance(receipt,str) or not receipt.strip():raise ValueError('Confirmed provider message ID required')
        receipt=receipt.strip()
        with self.conn:
            row=self.conn.execute('SELECT recipient,status,receipt,draft_id FROM packets WHERE id=?',(ident,)).fetchone()
            if not row:raise ValueError('Unknown packet')
            # This imports an observed historical receipt; it never sends mail.
            # A later stop reply must block future reservations, not erase history.
            if row[1]=='sent':
                if row[2]!=receipt:raise ValueError('Conflicting send receipt')
                return False
            if row[1]!='sending':raise ValueError('A confirmed send requires a reserved attempt')
            if (row[3] and receipt==row[3].strip()) or re.fullmatch(r'r-?\d+',receipt):
                raise ValueError('Provider draft ID is not a send receipt')
            self.conn.execute("UPDATE packets SET status='sent',receipt=? WHERE id=?",(receipt,ident))
        return True
