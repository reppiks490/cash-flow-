"""Offline, supplied-evidence audit exports; never proof of sales or performance."""
from datetime import datetime, timezone
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

from .discovery import domain_name
from .private import private_path


NOTICE='Supplied evidence only. Business impact is not measured. No performance guarantee.'


def _text(value, name, limit=2000):
    if not isinstance(value,str) or not value.strip() or len(value)>limit:
        raise ValueError(f'{name} must be nonempty text within {limit} characters')
    if any(ord(c)<32 and c not in '\n\t' for c in value):
        raise ValueError(f'{name} contains control characters')
    return value.strip()


def _items(value, name, maximum):
    if not isinstance(value,list) or not 1<=len(value)<=maximum:
        raise ValueError(f'{name} requires 1–{maximum} items')
    return value


def _url(value):
    value=_text(value,'source URL',2000)
    if re.search(r'\s',value):raise ValueError('Source URL contains whitespace')
    p=urlsplit(value)
    if p.scheme!='https' or p.username or p.password or p.port not in (None,443):
        raise ValueError('Source URL must use public HTTPS without credentials')
    domain_name(p.hostname or '')
    return value


def validate_audit(payload):
    if not isinstance(payload,dict):raise ValueError('Audit must be an object')
    if type(payload.get('schema_version')) is not int or payload['schema_version']!=1:
        raise ValueError('Expected schema version 1')
    if payload.get('mode') not in ('specimen','review') or payload.get('reviewed') is not True:
        raise ValueError('Explicit specimen/review mode and supplied-evidence review are required')
    sources=[];ids=set()
    for source in _items(payload.get('sources'),'sources',10):
        if not isinstance(source,dict):raise ValueError('Source must be an object')
        ident=_text(source.get('id'),'source ID',64)
        if not re.fullmatch(r'[A-Za-z0-9_-]+',ident) or ident in ids:
            raise ValueError('Source IDs must be unique simple identifiers')
        observed=_text(source.get('observed_at'),'observation time',80)
        try:stamp=datetime.fromisoformat(observed.replace('Z','+00:00'))
        except ValueError:raise ValueError('Source observation timestamp must be ISO8601')
        if stamp.tzinfo is None or stamp.utcoffset() is None:
            raise ValueError('Source observation timestamp needs a timezone')
        sources.append(dict(id=ident,url=_url(source.get('url')),observed_at=observed,
                            excerpt=_text(source.get('excerpt'),'source excerpt',8000)))
        ids.add(ident)
    lookup={s['id']:s for s in sources};findings=[]
    for finding in _items(payload.get('findings'),'findings',8):
        if not isinstance(finding,dict):raise ValueError('Finding must be an object')
        ident=finding.get('source_id')
        if not isinstance(ident,str) or ident not in lookup:raise ValueError('Finding has an unknown source')
        quote=_text(finding.get('evidence_quote'),'evidence quote',1600)
        if quote not in lookup[ident]['excerpt']:raise ValueError('Evidence quote is absent from supplied source excerpt')
        priority=finding.get('priority')
        if priority not in ('P1','P2','P3'):raise ValueError('Priority must be P1/P2/P3; not a revenue score')
        findings.append(dict(source_id=ident,evidence_quote=quote,priority=priority,
            **{k:_text(finding.get(k),k,1600) for k in
               ('title','observation','impact_hypothesis','recommended_action','counter_evidence')}))
    return dict(schema_version=1,mode=payload['mode'],reviewed=True,
        company=_text(payload.get('company'),'company',200),
        objective=_text(payload.get('objective'),'objective',1600),sources=sources,
        findings=sorted(findings,key=lambda f:f['priority']),
        limitations=[_text(x,'limitation',1600) for x in _items(payload.get('limitations'),'limitations',8)])


def _label(report):
    return 'SPECIMEN - fictional, uncommissioned' if report['mode']=='specimen' else 'REVIEW - supplied observations, not commissioned delivery'


def _markdown(text):
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])',r'\\\1',escape(text,quote=False))


def render_markdown(report):
    lines=['# Opportunity clarity review','',_label(report),'',NOTICE,'',
           '## '+_markdown(report['company']),'',_markdown(report['objective']),'']
    lookup={s['id']:s for s in report['sources']}
    for n,f in enumerate(report['findings'],1):
        s=lookup[f['source_id']]
        lines.extend([f"## {n}. {f['priority']} - "+_markdown(f['title']),'',
            '**Observed quote:** '+_markdown(f['evidence_quote']),'',
            '**Supplied observation:** '+_markdown(f['observation']),'',
            '**Untested impact hypothesis:** '+_markdown(f['impact_hypothesis']),'',
            '**Recommended action:** '+_markdown(f['recommended_action']),'',
            '**Counter-evidence / check:** '+_markdown(f['counter_evidence']),'',
            '**Source:** '+_markdown(s['url'])+' | '+_markdown(s['observed_at']),''])
    lines.extend(['## Limitations','']+['- '+_markdown(x) for x in report['limitations']])
    lines.extend(['','## Supplied source excerpts',''])
    for s in report['sources']:
        lines.extend(['### '+s['id'],'',_markdown(s['url'])+' | '+_markdown(s['observed_at']),'',_markdown(s['excerpt']),''])
    return '\n'.join(lines)+'\n'


def render_html(report):
    e=escape;lookup={s['id']:s for s in report['sources']};cards=[]
    for n,f in enumerate(report['findings'],1):
        s=lookup[f['source_id']]
        parts=[f'<section><div class="tag">{n:02d} / {f["priority"]}</div><h2>{e(f["title"])}</h2>',
               f'<blockquote>{e(f["evidence_quote"])}</blockquote>']
        for key,label in [('observation','Supplied observation'),('impact_hypothesis','Untested impact hypothesis'),
                          ('recommended_action','Recommended action'),('counter_evidence','Counter-evidence / check')]:
            parts.append(f'<h3>{label}</h3><p>{e(f[key])}</p>')
        parts.append(f'<p class="source">Source: <a href="{e(s["url"],quote=True)}">{e(s["url"])}</a><br>Observed: {e(s["observed_at"])}</p></section>')
        cards.append(''.join(parts))
    sources=''.join(f'<section><h3>{e(s["id"])}</h3><p>{e(s["url"])}<br>{e(s["observed_at"])}</p><p>{e(s["excerpt"])}</p></section>' for s in report['sources'])
    limits=''.join('<li>'+e(x)+'</li>' for x in report['limitations'])
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Opportunity clarity review</title>
<style>body{{margin:0;background:#f4f5f2;color:#18272c;font:16px/1.6 system-ui,sans-serif}}main{{max-width:800px;margin:auto;padding:48px 28px}}header{{border-top:7px solid #117b71;padding:30px 0}}h1{{font-size:42px;line-height:1.1;letter-spacing:-1px}}h2{{font-size:24px;line-height:1.25}}h3{{font-size:13px;text-transform:uppercase;letter-spacing:1px;margin-bottom:5px}}section{{background:white;padding:28px;margin:22px 0;border:1px solid #d5dfd9;border-radius:12px;break-inside:avoid}}blockquote{{margin:20px 0;padding:12px 18px;border-left:4px solid #117b71;background:#edf7f3}}.tag{{font-size:12px;letter-spacing:2px;color:#117b71;font-weight:700}}.notice,.source{{font-size:13px;color:#506168}}a{{color:#117b71;overflow-wrap:anywhere}}p{{overflow-wrap:anywhere}}@media print{{body{{background:white}}main{{padding:0}}section{{border-radius:0}}h1{{font-size:32px}}}}</style>
</head><body><main><header><div class="tag">PUBLIC EVIDENCE / ACTION REVIEW</div><h1>Opportunity clarity review</h1><h2>{e(report['company'])}</h2><p>{e(report['objective'])}</p><p class="notice">{e(_label(report))}<br>{NOTICE}</p></header>{''.join(cards)}<h2>Limitations</h2><ul>{limits}</ul><h2>Supplied source excerpts</h2>{sources}</main></body></html>'''


def _prepare_pdf(report):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    folder=Path(os.environ.get('MONEYFALL_FONT_DIR','/usr/share/fonts/truetype/dejavu'))
    paths=[folder/'DejaVuSans.ttf',folder/'DejaVuSans-Bold.ttf']
    if not all(p.is_file() for p in paths):
        raise ValueError('PDF export requires DejaVu Sans regular/bold fonts; set MONEYFALL_FONT_DIR')
    fonts=[TTFont('MoneyfallAuditRegular',str(paths[0])),TTFont('MoneyfallAuditBold',str(paths[1]))]
    coverage=set(fonts[0].face.charToGlyph)&set(fonts[1].face.charToGlyph)
    missing={ord(c) for c in json.dumps(report,ensure_ascii=False) if ord(c)>=32 and ord(c) not in coverage}
    if missing:
        codes=', '.join(f'U+{n:04X}' for n in sorted(missing)[:8])
        raise ValueError('PDF font lacks glyph coverage: '+codes+'; use HTML/Markdown export')
    for font in fonts:pdfmetrics.registerFont(font)


def _write_pdf(report,path):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='AuditTitle',fontName='MoneyfallAuditBold',fontSize=26,leading=30,textColor=colors.HexColor('#18272c'),spaceAfter=16))
    styles.add(ParagraphStyle(name='AuditBody',fontName='MoneyfallAuditRegular',fontSize=10.5,leading=15,spaceAfter=9,splitLongWords=True))
    styles.add(ParagraphStyle(name='AuditTag',fontName='MoneyfallAuditBold',fontSize=9,leading=12,textColor=colors.HexColor('#117b71'),spaceAfter=9))
    styles.add(ParagraphStyle(name='AuditHeading',fontName='MoneyfallAuditBold',fontSize=17,leading=21,spaceAfter=12))
    styles.add(ParagraphStyle(name='AuditSource',fontName='MoneyfallAuditRegular',fontSize=8.5,leading=12,textColor=colors.HexColor('#506168'),spaceAfter=9,splitLongWords=True))
    def p(text,style='AuditBody'):return Paragraph(escape(text).replace('\n','<br/>'),styles[style])
    story=[p('PUBLIC EVIDENCE / ACTION REVIEW','AuditTag'),p('Opportunity clarity review','AuditTitle'),
           p(report['company'],'AuditHeading'),p(report['objective']),p(_label(report),'AuditTag'),
           p(NOTICE,'AuditSource'),Spacer(1,12)]
    lookup={s['id']:s for s in report['sources']}
    for n,f in enumerate(report['findings'],1):
        if n>1:story.append(PageBreak())
        s=lookup[f['source_id']]
        story.extend([p(f'{n:02d} / {f["priority"]}','AuditTag'),p(f['title'],'AuditHeading'),p('Observed quote: '+f['evidence_quote'])])
        for key,label in [('observation','Supplied observation'),('impact_hypothesis','Untested impact hypothesis'),
                          ('recommended_action','Recommended action'),('counter_evidence','Counter-evidence / check')]:
            story.extend([p(label.upper(),'AuditTag'),p(f[key])])
        story.append(p('Source: '+s['url']+' | Observed: '+s['observed_at'],'AuditSource'))
    story.extend([PageBreak(),p('Limitations & source record','AuditHeading')])
    for item in report['limitations']:story.append(p('- '+item))
    for s in report['sources']:
        story.extend([Spacer(1,10),p(s['id'].upper(),'AuditTag'),p(s['url']+' | '+s['observed_at'],'AuditSource'),p(s['excerpt'])])
    def page(canvas,doc):
        canvas.setStrokeColor(colors.HexColor('#117b71'));canvas.setLineWidth(3)
        canvas.line(44,A4[1]-30,A4[0]-44,A4[1]-30)
        canvas.setFont('MoneyfallAuditRegular',8);canvas.setFillColor(colors.HexColor('#506168'))
        canvas.drawString(44,25,report['mode'].upper()+' / supplied evidence; impact not measured')
        canvas.drawRightString(A4[0]-44,25,str(doc.page))
    SimpleDocTemplate(str(path),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=46,bottomMargin=44,
                      title='Opportunity clarity review',author='MONEYFALL').build(story,onFirstPage=page,onLaterPages=page)


def write_audit(payload,output,repo,*,pdf=False,source_bytes=None):
    report=validate_audit(payload)
    canonical=json.dumps(payload,sort_keys=True,allow_nan=False).encode()
    if source_bytes is not None:
        if not isinstance(source_bytes,bytes) or len(source_bytes)>500000:
            raise ValueError('Source bytes must be a bounded original JSON input')
        if json.dumps(json.loads(source_bytes),sort_keys=True,allow_nan=False).encode()!=canonical:
            raise ValueError('Source bytes differ from supplied payload')
    input_bytes=canonical if source_bytes is None else source_bytes
    output=private_path(output,repo)
    if output.exists():raise FileExistsError('Use a new private output directory; existing exports are preserved')
    if pdf:
        try:_prepare_pdf(report)
        except ImportError:raise ValueError('PDF export requires optional ReportLab')
    output.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    output.mkdir(mode=0o700)
    try:
        for name,text in [('audit.md',render_markdown(report)),('audit.html',render_html(report))]:
            with (output/name).open('x',encoding='utf-8') as stream:stream.write(text)
            os.chmod(output/name,0o600)
        if pdf:_write_pdf(report,output/'audit.pdf');os.chmod(output/'audit.pdf',0o600)
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir())}
        manifest=dict(schema_version=1,mode=report['mode'],specimen=report['mode']=='specimen',
            generated_at=datetime.now(timezone.utc).isoformat(),
            input_sha256=hashlib.sha256(input_bytes).hexdigest(),
            input_hash_basis='canonical_supplied_payload' if source_bytes is None else 'exact_source_bytes',
            normalized_report_sha256=hashlib.sha256(json.dumps(report,sort_keys=True,allow_nan=False).encode()).hexdigest(),
            files=hashes,authority='production only; no send/payment/delivery receipt')
        with (output/'manifest.json').open('x',encoding='utf-8') as stream:json.dump(manifest,stream,indent=2)
        os.chmod(output/'manifest.json',0o600)
    except Exception:
        shutil.rmtree(output)
        raise
    return dict(mode=report['mode'],findings=len(report['findings']),files=sorted(hashes)+['manifest.json'])
