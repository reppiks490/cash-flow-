"""Revenue Recovery synthetic-only MVP. Standard library; no external communications."""
import argparse
import json
import sqlite3
from pathlib import Path

SCHEMA_VERSION = "rre.v1"
DDL = """
CREATE TABLE IF NOT EXISTS leads (
 id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, source TEXT NOT NULL,
 service TEXT NOT NULL, consent INTEGER NOT NULL CHECK(consent IN (0,1)),
 synthetic INTEGER NOT NULL CHECK(synthetic = 1),
 status TEXT NOT NULL CHECK(status IN ('new','qualified','suppressed'))
);
CREATE TABLE IF NOT EXISTS drafts (
 lead_id TEXT PRIMARY KEY REFERENCES leads(id), body TEXT NOT NULL,
 approval TEXT NOT NULL DEFAULT 'pending' CHECK(approval IN ('pending','approved'))
);
CREATE TABLE IF NOT EXISTS events (
 event_id TEXT PRIMARY KEY, lead_id TEXT NOT NULL REFERENCES leads(id),
 kind TEXT NOT NULL CHECK(kind IN ('appointment_mock','crm_mock')),
 synthetic INTEGER NOT NULL CHECK(synthetic = 1)
);
"""
def connect(path=":memory:"):
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(DDL)
    return db

def intake(db, lead):
    required = ("id", "tenant_id", "source", "service", "consent", "synthetic")
    if any(k not in lead for k in required):
        raise ValueError("missing required lead field")
    if lead["synthetic"] is not True or type(lead["consent"]) is not bool:
        raise ValueError("synthetic=true and boolean consent required")
    if not all(isinstance(lead[k], str) and lead[k].strip() for k in ("id","tenant_id","source","service")):
        raise ValueError("nonempty identifiers/source/service required")
    status = "qualified" if lead["consent"] and lead["service"].lower() in ("repair", "maintenance", "installation") else ("suppressed" if not lead["consent"] else "new")
    try:
        db.execute("INSERT INTO leads VALUES (?,?,?,?,?,?,?)",
                   (lead["id"],lead["tenant_id"],lead["source"],lead["service"],int(lead["consent"]),1,status))
    except sqlite3.IntegrityError as exc:
        raise ValueError("duplicate lead id") from exc
    if status == "qualified":
        db.execute("INSERT INTO drafts(lead_id,body) VALUES (?,?)",
                   (lead["id"],"Draft for human review only: Please contact us if you would like to discuss your HVAC "+lead["service"]+"."))
    db.commit()
    return {"id":lead["id"],"status":status,"schema":SCHEMA_VERSION}

def mock_event(db, event_id, lead_id, kind):
    if kind not in ("appointment_mock", "crm_mock"):
        raise ValueError("only mock events allowed")
    row=db.execute("SELECT status FROM leads WHERE id=?",(lead_id,)).fetchone()
    if not row or row[0] != "qualified":
        raise ValueError("only qualified synthetic leads may receive mock events")
    db.execute("INSERT INTO events VALUES (?,?,?,1)",(event_id,lead_id,kind))
    db.commit()

def report(db, tenant_id):
    counts=dict(db.execute("SELECT status,COUNT(*) FROM leads WHERE tenant_id=? GROUP BY status",(tenant_id,)).fetchall())
    drafts=db.execute("SELECT COUNT(*) FROM drafts d JOIN leads l ON l.id=d.lead_id WHERE l.tenant_id=?",(tenant_id,)).fetchone()[0]
    events=dict(db.execute("SELECT e.kind,COUNT(*) FROM events e JOIN leads l ON l.id=e.lead_id WHERE l.tenant_id=? GROUP BY e.kind",(tenant_id,)).fetchall())
    return {"schema":SCHEMA_VERSION,"tenant_id":tenant_id,"lead_counts":counts,"pending_or_approved_drafts":drafts,"mock_events":events,"verified_closed_revenue_cents":None,"verified_net_profit_cents":None,"synthetic":True}

def demo():
    db=connect()
    lead={"id":"synthetic-hvac-001","tenant_id":"synthetic-tenant","source":"synthetic-web-form","service":"repair","consent":True,"synthetic":True}
    outcome=intake(db,lead)
    mock_event(db,"synthetic-event-001",lead["id"],"crm_mock")
    return {"intake":outcome,"report":report(db,lead["tenant_id"]),"outbound_sent":False}

def main():
    parser=argparse.ArgumentParser(description="Offline synthetic HVAC revenue recovery demo")
    parser.add_argument("command",choices=["demo"])
    args=parser.parse_args()
    if args.command=="demo":
        print(json.dumps(demo(),indent=2,sort_keys=True))
if __name__=="__main__":
    main()
