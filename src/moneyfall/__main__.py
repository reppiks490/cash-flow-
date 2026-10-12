import argparse
import json
import hashlib
import os
import sys
import tempfile
from pathlib import Path

from .offers import brief
from .scoring import opportunity_score, readiness
from .sources import collect
from .store import KINDS, Store

ROOT = Path(__file__).resolve().parents[2]


def emit(data):
    print(json.dumps(data, indent=2, allow_nan=False))


def main():
    p=argparse.ArgumentParser(description='MONEYFALL ZERO private research and attribution CLI')
    p.add_argument('--state', default=os.environ.get('MONEYFALL_STATE', str(Path.home()/'.local/share/moneyfall/state.sqlite')))
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('rank')
    sub.add_parser('demo')
    sub.add_parser('metrics').add_argument('--opportunity')
    sub.add_parser('queue')
    c=sub.add_parser('collect')
    c.add_argument('provider',choices=['greenhouse','lever'])
    c.add_argument('token')
    b=sub.add_parser('brief')
    b.add_argument('signal_id')
    b.add_argument('--hypothesis',default='content-repurpose')
    b.add_argument('--opportunity',default='signal-driven-b2b')
    e=sub.add_parser('event')
    e.add_argument('id')
    e.add_argument('signal_id')
    e.add_argument('kind',choices=sorted(KINDS))
    e.add_argument('--amount',type=int,default=0)
    e.add_argument('--evidence',required=True)
    q=sub.add_parser('qualify')
    q.add_argument('signal_id')
    q.add_argument('evidence_file',help='Private JSON with dimensions and evidence URLs')
    args=p.parse_args()
    if args.command=='rank':
        opportunities=json.loads((ROOT/'config/opportunities.json').read_text())
        emit(dict(basis='scenario assumptions, not observed conversion rates', incumbent=opportunities['incumbent'],
                  ranking=sorted([dict(id=o['id'],score=opportunity_score(o['scenario']),
                                       basis=o['basis']) for o in opportunities['candidates']],
                                 key=lambda o:o['score'],reverse=True)))
        return
    if args.command=='demo':
        with tempfile.TemporaryDirectory() as tmp:
            db=Store(Path(tmp)/'demo.sqlite',repo=ROOT)
            db.ingest(dict(id='synthetic:1',company='Synthetic example',title='Video editor',
                           url='https://example.org',retrieved_at='2026-10-12T00:00:00Z'))
            db.event('demo-payment','synthetic:1','payment',14900,'synthetic receipt')
            db.event('demo-refund','synthetic:1','refund',4900,'synthetic refund')
            emit(dict(mode='synthetic',live_revenue_cents=0,metrics=db.metrics()))
            db.close()
        return
    db=Store(args.state,repo=ROOT)
    try:
        if args.command=='collect':
            signals=collect(args.provider,args.token)
            new=sum(db.ingest(s) for s in signals)
            emit(dict(provider=args.provider,board=args.token,matched=len(signals),new=new,
                      spending_cents=0,qualification='unverified candidates'))
        elif args.command=='queue':
            emit([dict(s,readiness=readiness(s.get('dimensions',{})),suppressed=db.suppressed(s['id'])) for s in db.signals()])
        elif args.command=='metrics':
            emit(db.metrics(opportunity_id=args.opportunity))
        elif args.command=='event':
            emit(dict(recorded=db.event(args.id,args.signal_id,args.kind,args.amount,args.evidence)))
        else:
            s=next((s for s in db.signals() if s['id']==args.signal_id),None)
            if s is None:
                raise ValueError('Unknown signal')
            if args.command=='brief':
                if db.suppressed(args.signal_id):
                    raise ValueError('Prospect is suppressed')
                text=brief(s,args.hypothesis)
                s['attribution']=dict(opportunity_id=args.opportunity,offer_id='revenue-strike-v1',
                                      asset_id=hashlib.sha256(text.encode()).hexdigest(),hypothesis=args.hypothesis)
                db.ingest(s)
                print(text)
            elif args.command=='qualify':
                evidence=json.loads(Path(args.evidence_file).read_text())
                if not isinstance(evidence,dict) or not isinstance(evidence.get('dimensions'),dict) or not isinstance(evidence.get('evidence'),dict):
                    raise ValueError('Qualification requires dimension and evidence mappings')
                score=readiness(evidence['dimensions'])
                for k,v in evidence['dimensions'].items():
                    proof=evidence['evidence'].get(k)
                    if v is not None and (not isinstance(proof,str) or not proof.strip()):
                        raise ValueError(f'Missing supporting evidence for {k}')
                s.update(dimensions=evidence['dimensions'],qualification_evidence=evidence['evidence'])
                db.ingest(s)
                emit(score)
    finally:
        db.close()


if __name__=='__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as exc:
        print(f'Error: {exc}',file=sys.stderr)
        sys.exit(1)
