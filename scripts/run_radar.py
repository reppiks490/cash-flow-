"""Resume-safe domain screening. Private state only; never sends messages."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from pathlib import Path
from urllib.robotparser import RobotFileParser

from moneyfall.discovery import classify,coverage,domain_name,extract_page
from moneyfall.network import AGENT,fetch_public
from moneyfall.store import Store


def scan(company,fetched=None):
    domain=domain_name(company['domain'])
    url=f'https://{domain}/'
    result=dict(id='website:'+domain,company=domain,organization=company.get('organization',domain),
                title='Public company service screening',url=url,provider='public-website',
                retrieved_at=datetime.now(timezone.utc).isoformat(),qualified=False)
    try:
        if fetched is not None:
            response=dict(url=fetched['url'],text=fetched['html'],content_type='text/html')
            if domain_name(__import__('urllib.parse',fromlist=['urlparse']).urlparse(response['url']).hostname or '')!=domain:
                raise ValueError('Fetched source does not match candidate domain')
            if len(response['text'].encode())>2_000_000:raise ValueError('Imported page too large')
            result['retrieved_at']=fetched['fetched_at']
        else:
            response=None
        try:
            if response is None:
                robots=fetch_public(url+'robots.txt',limit=100_000,timeout=8)
                rp=RobotFileParser();rp.parse(robots['text'].splitlines())
                if not rp.can_fetch(AGENT,url):raise PermissionError('robots.txt disallows research read')
        except ValueError as exc:
            if 'HTTP 404' not in str(exc):raise
        if response is None:response=fetch_public(url)
        if 'html' not in response['content_type']:raise ValueError('Homepage was not HTML')
        page=extract_page(response['text'])
        result.update(url=response['url'],title=page['title'] or result['title'],
                      compatibility=classify(page['text']),website_text=page['text'],
                      public_emails=[e for e in page['emails'] if e.lower().endswith('@'+domain)],
                      links=page['links'],scan_status='review_required')
    except (ValueError,PermissionError,OSError) as exc:
        result.update(scan_status='failed',error=str(exc),compatibility={'route':'review','send_ready':False})
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('companies',type=Path)
    p.add_argument('--state',type=Path,required=True)
    p.add_argument('--limit',type=int,default=100)
    p.add_argument('--workers',type=int,default=6)
    p.add_argument('--reported',type=int,default=9140)
    p.add_argument('--fetched',type=Path,help='Private JSON pages collected through an available licensed connector')
    args=p.parse_args()
    if not 1<=args.workers<=8 or not 1<=args.limit<=10000:raise ValueError('Invalid bounded scan budget')
    source=json.loads(args.companies.read_text())
    companies={domain_name(c['domain']):c for c in source if c.get('domain')}
    repo=Path(__file__).resolve().parents[1]
    db=Store(args.state,repo=repo)
    processed={s['company'] for s in db.signals() if s.get('provider')=='public-website' and s.get('scan_status')!='failed'}
    pending=[c for domain,c in companies.items() if domain not in processed and
             (args.fetched is None or (args.fetched/(domain+'.json')).exists())][:args.limit]
    stats={'processed_this_run':0,'failed':0,'suggested_fit':0,'review':0,'rejected':0}
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for result in pool.map(lambda c:scan(c,json.loads((args.fetched/(domain_name(c['domain'])+'.json')).read_text()) if args.fetched else None),pending):
                db.ingest(result)
                stats['processed_this_run']+=1
                route=result['compatibility']['route']
                stats['failed' if result['scan_status']=='failed' else 'suggested_fit' if route in ('white-label-content','local-creative') else 'rejected' if route=='reject' else 'review']+=1
        stats.update(coverage(args.reported,list(companies.values())))
        successful={domain_name(s['company']) for s in db.signals() if s.get('provider')=='public-website' and s.get('scan_status')!='failed'}
        stats['remaining_unscanned']=len(set(companies)-successful)
        print(json.dumps(stats,indent=2))
    finally:db.close()


if __name__=='__main__':main()
