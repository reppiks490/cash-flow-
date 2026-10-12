"""Private order lifecycle CLI; never stores a payment credential in git."""
import argparse
import json
import os
from pathlib import Path
from moneyfall.orders import Orders,verify_stripe


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--state',type=Path,required=True)
    sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('create');c.add_argument('id');c.add_argument('signal');c.add_argument('--scope',required=True);c.add_argument('--price-cents',type=int,default=14900)
    c=sub.add_parser('payment');c.add_argument('id');c.add_argument('--receipt',required=True);c.add_argument('--amount-cents',type=int,required=True)
    c=sub.add_parser('refund');c.add_argument('id');c.add_argument('--receipt',required=True);c.add_argument('--amount-cents',type=int,required=True)
    c=sub.add_parser('assets');c.add_argument('id');c.add_argument('--approved-reference',required=True)
    c=sub.add_parser('status');c.add_argument('id')
    c=sub.add_parser('fulfill');c.add_argument('id');c.add_argument('folder',type=Path)
    c=sub.add_parser('delivered');c.add_argument('id');c.add_argument('--receipt',required=True)
    c=sub.add_parser('stripe-import');c.add_argument('payload',type=Path);c.add_argument('--signature',required=True)
    args=p.parse_args();db=Orders(args.state,repo=Path(__file__).resolve().parents[1])
    try:
        if args.command=='create':db.create_order(args.id,args.signal,scope=args.scope,price_cents=args.price_cents)
        elif args.command=='payment':db.payment(args.id,args.receipt,args.amount_cents)
        elif args.command=='refund':db.refund(args.id,args.receipt,args.amount_cents)
        elif args.command=='assets':db.assets(args.id,licensed=True,reference=args.approved_reference)
        elif args.command=='fulfill':db.fulfill(args.id,args.folder)
        elif args.command=='delivered':db.delivered(args.id,args.receipt)
        elif args.command=='stripe-import':
            event=verify_stripe(args.payload.read_bytes(),args.signature,os.environ.get('MONEYFALL_STRIPE_WEBHOOK_SECRET',''))
            print(json.dumps(dict(recorded=db.payment(event['order_id'],event['receipt'],event['amount_cents']))));return
        print(json.dumps(dict(order=db.get_order(args.id),ready=db.ready(args.id)),indent=2))
    finally:db.close()


if __name__=='__main__':main()
