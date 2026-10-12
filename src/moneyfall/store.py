"""Private SQLite state; never export operational records to public CI."""
import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

KINDS = {'draft', 'sent', 'delivered', 'bounced', 'reply', 'positive_reply',
         'meeting', 'payment', 'refund', 'cost', 'fulfilled', 'suppressed', 'credit_spend'}
MONEY = {'payment', 'refund', 'cost'}


class Store:
    def __init__(self, path, *, repo):
        self.path = Path(path).expanduser().resolve()
        if self.path.is_relative_to(Path(repo).resolve()):
            raise ValueError('Operational state must live outside the public checkout')
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        os.chmod(self.path, 0o600)
        self.conn = sqlite3.connect(self.path)
        self.conn.execute('PRAGMA foreign_keys=ON')
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS signals (
                id TEXT PRIMARY KEY, payload TEXT NOT NULL, first_seen TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, signal_id TEXT REFERENCES signals(id),
                kind TEXT NOT NULL, amount INTEGER NOT NULL,
                evidence TEXT NOT NULL, observed_at TEXT NOT NULL);
        ''')
        if 'attribution' not in {row[1] for row in self.conn.execute('PRAGMA table_info(events)')}:
            self.conn.execute("ALTER TABLE events ADD COLUMN attribution TEXT NOT NULL DEFAULT '{}'")
            self.conn.commit()

    def close(self):
        self.conn.close()

    def ingest(self, signal):
        for key in ('id', 'company', 'title', 'url', 'retrieved_at'):
            if not isinstance(signal.get(key), str) or not signal[key].strip():
                raise ValueError(f'Missing signal field: {key}')
        with self.conn:
            old = self.conn.execute('SELECT payload FROM signals WHERE id=?', (signal['id'],)).fetchone()
            new = old is None
            if old:
                previous=json.loads(old[0])
                if any(previous.get(k)!=signal.get(k) for k in ('company','title','url')):
                    previous.pop('dimensions',None)
                    previous.pop('qualification_evidence',None)
                signal=dict(previous,**signal)
            self.conn.execute('''INSERT INTO signals VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET payload=excluded.payload''',
                (signal['id'], json.dumps(signal, allow_nan=False), signal['retrieved_at']))
        return new

    def signals(self):
        return [dict(json.loads(p), first_seen=f) for p, f in self.conn.execute(
            'SELECT payload, first_seen FROM signals ORDER BY first_seen DESC, id')]

    def event(self, ident, signal_id, kind, amount=0, evidence=''):
        if not isinstance(evidence,str) or not isinstance(ident,str):
            raise ValueError('Evidence and event ID must be strings')
        evidence, ident = evidence.strip(), ident.strip()
        if kind not in KINDS or not ident or not evidence.strip():
            raise ValueError('Event requires valid kind, ID and observed evidence')
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
            raise ValueError('Amounts must be nonnegative integer cents/credits')
        if kind not in MONEY | {'credit_spend'} and amount:
            raise ValueError('Nonfinancial event cannot carry an amount')
        if kind in MONEY and amount == 0:
            raise ValueError('Money event must be positive')
        if not self.conn.execute('SELECT 1 FROM signals WHERE id=?', (signal_id,)).fetchone():
            raise ValueError('Unknown signal')
        existing = self.conn.execute('SELECT signal_id,kind,amount,evidence FROM events WHERE id=?', (ident,)).fetchone()
        if existing:
            if existing != (signal_id, kind, amount, evidence):
                raise ValueError('Conflicting duplicate event ID')
            return False
        if kind in MONEY and self.conn.execute('SELECT 1 FROM events WHERE kind=? AND evidence=?', (kind,evidence)).fetchone():
            raise ValueError('Financial receipt already recorded')
        if kind == 'refund':
            balance = self.conn.execute('''SELECT COALESCE(SUM(CASE WHEN kind='payment'
                THEN amount WHEN kind='refund' THEN -amount ELSE 0 END),0)
                FROM events WHERE signal_id=?''', (signal_id,)).fetchone()[0]
            if amount > balance:
                raise ValueError('Refund exceeds collected cash for signal')
        with self.conn:
            signal=json.loads(self.conn.execute('SELECT payload FROM signals WHERE id=?',(signal_id,)).fetchone()[0])
            self.conn.execute('INSERT INTO events VALUES (?,?,?,?,?,?,?)', (
                ident, signal_id, kind, amount, evidence, datetime.now(timezone.utc).isoformat(),
                json.dumps(signal.get('attribution',{}),allow_nan=False)))
        return True

    def suppressed(self, signal_id):
        identities = {s['id']: s['company'].strip().casefold() for s in self.signals()}
        company = identities.get(signal_id)
        return any(identities.get(sid) == company for sid, in self.conn.execute(
            "SELECT signal_id FROM events WHERE kind IN ('suppressed','bounced')")) if company else False

    def metrics(self, *, opportunity_id=None):
        identities = {s['id']: s['company'].strip().casefold() for s in self.signals()}
        totals, companies = {}, {}
        cohort={s['company'].strip().casefold() for s in self.signals()
                if opportunity_id is None or s.get('attribution',{}).get('opportunity_id')==opportunity_id}
        for kind, amount, sid, attribution in self.conn.execute('SELECT kind,amount,signal_id,attribution FROM events'):
            if opportunity_id is not None and json.loads(attribution).get('opportunity_id') != opportunity_id:
                continue
            cohort.add(identities[sid])
            totals[kind] = totals.get(kind, 0) + amount
            companies.setdefault(kind,set()).add(identities[sid])
        counts = {k:len(v) for k,v in companies.items()}
        prospects = len(cohort)
        revenue = totals.get('payment', 0) - totals.get('refund', 0)
        profit = revenue - totals.get('cost', 0)
        return dict(prospects=prospects, signals=len(identities), paid_prospects=counts.get('payment', 0),
                    net_revenue_cents=revenue, gross_profit_cents=profit,
                    revenue_per_100_prospects_cents=100 * revenue / prospects if prospects else 0,
                    profit_per_100_prospects_cents=100 * profit / prospects if prospects else 0,
                    events_by_kind=counts, credits_spent=totals.get('credit_spend', 0))
