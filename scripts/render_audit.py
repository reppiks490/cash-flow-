"""Produce private evidence-linked reports; never fetches, sends or charges."""
import argparse
import json
from pathlib import Path
import sys

from moneyfall.audits import write_audit


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('output',type=Path)
    parser.add_argument('--pdf',action='store_true',help='Optional ReportLab export')
    args=parser.parse_args()
    with args.input.open('rb') as stream:raw=stream.read(500001)
    if len(raw)>500000:raise ValueError('Input exceeds 500000-byte limit')
    summary=write_audit(json.loads(raw),args.output,Path(__file__).resolve().parents[1],pdf=args.pdf,source_bytes=raw)
    print(json.dumps(summary,allow_nan=False))


if __name__=='__main__':
    try:main()
    except (ValueError,OSError) as exc:
        print('Error: '+str(exc),file=sys.stderr)
        sys.exit(1)
