"""Public job-board GET ingestion. No candidate data or application submission."""
import json
import re
from datetime import datetime, timezone
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROLE = re.compile(r'\b(marketing|marketer|growth|social|video|content|creative|editor|sales)\b', re.I)


def source_url(provider, token):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', token):
        raise ValueError('Invalid public board token')
    if provider == 'greenhouse':
        return f'https://boards-api.greenhouse.io/v1/boards/{token}/jobs'
    if provider == 'lever':
        return f'https://api.lever.co/v0/postings/{token}?mode=json'
    raise ValueError('Unsupported public provider')


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected redirect from public board API')


def collect(provider, token):
    url = source_url(provider, token)
    request = Request(url, headers={'Accept': 'application/json', 'User-Agent': 'MoneyfallResearch/0.1'})
    with build_opener(NoRedirect).open(request, timeout=20) as response:
        raw = response.read(5_000_001)
    if len(raw) > 5_000_000:
        raise ValueError('Board response exceeds 5 MB limit')
    return normalize(provider, token, json.loads(raw), datetime.now(timezone.utc).isoformat())


def normalize(provider, token, payload, retrieved_at):
    source_url(provider, token)
    jobs = payload.get('jobs') if provider == 'greenhouse' and isinstance(payload, dict) else payload
    if not isinstance(jobs, list):
        raise ValueError('Unexpected public job-board response shape')
    result = []
    for job in jobs:
        if not isinstance(job, dict):
            raise ValueError('Unexpected job record')
        title = job.get('title' if provider == 'greenhouse' else 'text', '')
        if not isinstance(title, str) or not ROLE.search(title):
            continue
        ident = job.get('id')
        url = job.get('absolute_url' if provider == 'greenhouse' else 'hostedUrl')
        if ident is None or not isinstance(url, str) or not url.startswith('https://'):
            raise ValueError('Job missing identifier or HTTPS evidence URL')
        if provider == 'greenhouse':
            source_time, kind = job.get('updated_at'), 'updated'
        else:
            timestamp = job.get('createdAt')
            source_time = datetime.fromtimestamp(timestamp / 1000, timezone.utc).isoformat() if timestamp is not None else None
            kind = 'created'
        result.append(dict(id=f'{provider}:{token}:{ident}', provider=provider,
                           company=token, title=title, url=url, source_time=source_time,
                           source_time_kind=kind if source_time else 'unavailable',
                           retrieved_at=retrieved_at, signal='public_hiring'))
    return result
