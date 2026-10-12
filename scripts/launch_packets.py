"""Build reviewable private packets; credentials and sending stay in connectors."""
import argparse
import hashlib
import json
from pathlib import Path
from moneyfall.launch import LaunchStore,make_packet


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--profile',type=Path,required=True)
    p.add_argument('--prospects',type=Path,required=True)
    p.add_argument('--state',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    repo=Path(__file__).resolve().parents[1]
    if args.output.resolve().is_relative_to(repo):raise ValueError('Packets must be saved outside public checkout')
    profile=json.loads(args.profile.read_text())
    prospects=json.loads(args.prospects.read_text())
    db=LaunchStore(args.state,repo=repo)
    args.output.mkdir(parents=True,exist_ok=True,mode=0o700)
    summaries=[]
    try:
        for prospect in prospects:
            file=Path(prospect['proof_path'])
            if hashlib.sha256(file.read_bytes()).hexdigest()!=prospect['proof_sha256']:raise ValueError('Proof changed after review')
            packet=make_packet(profile,prospect,intro=prospect['intro'])
            if db.is_suppressed(packet['to']) or db.suppressed(packet['signal_id']):
                packet['gates'].append('suppression')
            db.save(packet)
            (args.output/(packet['id']+'.json')).write_text(json.dumps(packet,indent=2))
            summaries.append(dict(id=packet['id'],company=packet['company'],gates=packet['gates']))
        print(json.dumps(summaries,indent=2))
    finally:db.close()


if __name__=='__main__':main()


