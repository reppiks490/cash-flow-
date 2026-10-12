"""Render original typography specimens; no client logos, photos or results."""
import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path

from PIL import Image,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from moneyfall.private import private_path

FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
BOLD=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')


def wrap(text,font,width):
    if width<=0:raise ValueError('Text width must be positive')
    lines=[];line=''
    for word in text.split():
        if font.getlength(word)>width:
            if line:lines.append(line);line=''
            chunk=''
            for char in word:
                if font.getlength(char)>width:raise ValueError('Glyph cannot fit available width')
                if font.getlength(chunk+char)>width:lines.append(chunk);chunk=char
                else:chunk+=char
            line=chunk
        else:
            candidate=(line+' '+word).strip()
            if font.getlength(candidate)>width and line:lines.append(line);line=word
            else:line=candidate
    if line:lines.append(line)
    return lines


def render_card(card,index,folder,accent,*,specimen=True):
    from PIL import ImageColor
    layout=card.get('layout','statement')
    if layout not in ('statement','editorial','split'):raise ValueError('Unknown portrait layout')
    if not isinstance(accent,str) or len(accent)>80:raise ValueError('Invalid accent color')
    try:rgb=ImageColor.getrgb(accent)
    except (ValueError,TypeError):raise ValueError('Invalid accent color')
    if len(rgb)!=3:raise ValueError('Accent color must be opaque')
    accent='#'+''.join(f'{n:02x}' for n in rgb)
    # Use the foreground with the greater luminance contrast on accent panels.
    def luminance(color):
        channels=[n/255 for n in color]
        linear=[n/12.92 if n<=0.04045 else ((n+0.055)/1.055)**2.4 for n in channels]
        return sum(n*weight for n,weight in zip(linear,(0.2126,0.7152,0.0722)))
    accent_luminance=luminance(rgb)
    dark_luminance=luminance((16,26,35))
    light_luminance=luminance((243,248,250))
    def contrast(a,b):return (max(a,b)+0.05)/(min(a,b)+0.05)
    dark_contrast=contrast(accent_luminance,dark_luminance)
    light_contrast=contrast(accent_luminance,light_luminance)
    accent_ink='#101a23' if dark_contrast>=light_contrast else '#f3f8fa'
    for key,limit in [('headline',500),('body',700),('cta',200)]:
        if not isinstance(card.get(key),str) or not card[key].strip() or len(card[key])>limit:
            raise ValueError('Missing or excessive portrait copy')
    if '\n' in card['cta'] or '\r' in card['cta']:raise ValueError('CTA must fit one line')
    width,height=1080,1920
    light=layout=='editorial'
    bg='#f4f1e9' if light else '#101a23'
    ink='#152831' if light else '#f3f8fa'
    muted='#50616b' if light else '#b8cbd6'
    outline='#c5d1cd' if light else '#2b414e'
    tiny=ImageFont.truetype(str(FONT),28)
    small=ImageFont.truetype(str(FONT),39)
    title_size=86 if layout=='split' else 91
    titlefont=ImageFont.truetype(str(BOLD),title_size)
    bodyfont=ImageFont.truetype(str(FONT),47)
    ctafont=ImageFont.truetype(str(BOLD),37)
    title_y=460 if layout=='split' else 500
    title_step=106 if layout=='split' else 116
    title_ink=accent_ink if layout=='split' else ink
    titles=wrap(card['headline'],titlefont,870)
    if len(titles)>5:raise ValueError('Headline is too long for portrait card')
    body_y=max(1130,title_y+len(titles)*title_step+80)
    bodies=wrap(card['body'],bodyfont,850)
    if body_y+len(bodies)*64>1540:raise ValueError('Body is too long for portrait card')
    if ctafont.getlength(card['cta'])>820:raise ValueError('CTA is too long')
    label='ORIGINAL SPEC CONCEPT' if specimen else 'APPROVED CLIENT CONCEPT'
    footer='UNCOMMISSIONED SAMPLE / NO RESULTS CLAIMED' if specimen else 'CLIENT CONTENT KIT / REVIEW BEFORE PUBLISHING'
    image=Image.new('RGB',(width,height),bg);draw=ImageDraw.Draw(image)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920" data-layout="{layout}">']
    def rect(x,y,w,h,fill,*,radius=0,stroke=None):
        draw.rounded_rectangle((x,y,x+w,y+h),radius=radius,fill=fill,outline=stroke,width=2)
        attrs=f'fill="{fill or "none"}"'+(f' stroke="{stroke}" stroke-width="2"' if stroke else '')
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" {attrs}/>')
    def text(x,y,value,font,size,color,*,bold=False):
        draw.text((x,y),value,font=font,fill=color,anchor='lt')
        weight='bold' if bold else 'normal'
        svg.append(f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans, sans-serif" font-weight="{weight}" font-size="{size}" dominant-baseline="text-before-edge">{html.escape(value)}</text>')
    rect(0,0,1080,1920,bg)
    if layout=='statement':
        for y in range(0,height,80):
            draw.line((0,y,width,y),fill='#14232e',width=1)
            svg.append(f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#14232e"/>')
        rect(70,80,940,1760,None,radius=40,stroke=outline)
        rect(100,142,160,12,accent)
    elif layout=='editorial':
        rect(70,80,940,1760,None,radius=12,stroke=outline)
        rect(100,140,12,280,accent)
        numberfont=ImageFont.truetype(str(BOLD),150)
        text(760,170,f'{index:02d}',numberfont,150,'#d6dfd7',bold=True)
    else:
        rect(70,80,940,1760,None,radius=40,stroke=outline)
        rect(70,410,940,640,accent,radius=24)
        rect(100,142,160,12,accent)
    label_x=140 if light else 100
    text(label_x,194,label,tiny,28,muted)
    text(label_x,306,f'{index:02d} / CONTENT PILOT',small,39,'#152831' if light else accent)
    for n,line in enumerate(titles):text(100,title_y+n*title_step,line,titlefont,title_size,title_ink,bold=True)
    for n,line in enumerate(bodies):text(100,body_y+n*64,line,bodyfont,47,muted)
    rect(100,1580,880,110,accent,radius=18)
    text(130,1610,card['cta'],ctafont,37,accent_ink,bold=True)
    text(100,1754,footer,tiny,28,muted)
    svg.append('</svg>')
    png=folder/f'card-{index:03}.png';image.save(png)
    (folder/f'card-{index:03}.svg').write_text('\n'.join(svg))
    return png


def pdf(job,images,path):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('MoneyfallProofRegular',str(FONT)))
    pdfmetrics.registerFont(TTFont('MoneyfallProofBold',str(BOLD)))
    c=canvas.Canvas(str(path),pagesize=(612,792));c.setTitle('Original content pilot - '+job['company'])
    c.setFillColor(HexColor('#101a23'));c.rect(0,0,612,792,fill=1,stroke=0)
    c.setFillColor(HexColor(job['accent']));c.setFont('MoneyfallProofBold',10)
    specimen=job.get('specimen',True)
    c.drawString(40,752,'MONEYFALL / ORIGINAL SPECIMEN' if specimen else 'MONEYFALL / CLIENT CONTENT KIT')
    company_title=job['company'][:43]
    title_width=pdfmetrics.stringWidth(company_title,'MoneyfallProofBold',22)
    title_size=min(22,22*532/title_width) if title_width else 22
    c.setFillColor(HexColor('#f3f8fa'));c.setFont('MoneyfallProofBold',title_size)
    c.drawString(40,710,company_title)
    c.setFont('MoneyfallProofRegular',10);c.setFillColor(HexColor('#b8cbd6'))
    for n,line in enumerate(wrap(job['observed'],ImageFont.truetype(str(FONT),10),520)):
        c.drawString(40,682-14*n,line)
    for i,image in enumerate(images):c.drawImage(ImageReader(image),40+i*178,335,width=166,height=295,mask='auto')
    c.setFont('MoneyfallProofBold',14);c.setFillColor(HexColor('#f3f8fa'));c.drawString(40,296,'A $149 white-label content pilot')
    c.setFont('MoneyfallProofRegular',10);c.setFillColor(HexColor('#b8cbd6'))
    scope=['3 portrait graphics + editable SVGs; 1 caption-led 15-second motion preview.',
           '3 captions and CTA options; one revision; no subscription or ad spend.',
           '48-hour delivery after accepted brief, payment and approved brand assets.',
           'Spec work only. No claimed client relationship, leads or revenue outcomes.' if specimen else 'Commissioned content kit. Review approved brand claims before publishing.',
           'Filming, voiceover, account access and publishing are outside this scope.']
    for i,line in enumerate(scope):c.drawString(40,273-i*17,line)
    c.setFont('MoneyfallProofBold',10);c.drawString(40,150,'Why this concept fits')
    c.setFont('MoneyfallProofRegular',9)
    for n,line in enumerate(wrap(job['hypothesis'],ImageFont.truetype(str(FONT),9),520)):
        c.drawString(40,133-13*n,line)
    c.setFillColor(HexColor('#8ea6b4'));c.setFont('MoneyfallProofRegular',7)
    c.drawString(40,60,'Original copy and artwork; use supplied brand assets only with permission.')
    # Keep a clickable source with a short display label for long URLs.
    c.drawString(40,45,'Public evidence: '+job['source_url'].split('/')[2])
    c.linkURL(job['source_url'],(40,40,570,56),relative=0,thickness=0)
    c.showPage();c.save()


def render(job,folder,*,video=True):
    folder=private_path(folder,Path(__file__).resolve().parents[1])
    from urllib.parse import urlparse
    if urlparse(job['source_url']).scheme!='https':raise ValueError('Source link must use HTTPS')
    if len(job['observed'])>220 or len(job['hypothesis'])>280:raise ValueError('Proof context exceeds page layout budget')
    folder.mkdir(parents=True,exist_ok=True)
    specimen=job.get('specimen',True)
    images=[render_card(card,i,folder,job['accent'],specimen=specimen) for i,card in enumerate(job['cards'],1)]
    if len(images)!=3:raise ValueError('A kit requires exactly three cards')
    pdf(job,images,folder/'proof.pdf')
    contact=Image.new('RGB',(1080,640),'#101a23')
    for i,image in enumerate(images):contact.paste(Image.open(image).resize((330,587)),(25+i*355,25))
    contact.save(folder/'contact-sheet.png')
    (folder/'captions.md').write_text('# Original caption options\n\n'+'\n\n'.join(f'{i}. {card["caption"]}\nCTA: {card["cta"]}' for i,card in enumerate(job['cards'],1)))
    if video:
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','1/5','-i',str(folder/'card-%03d.png'),
                        '-vf',"zoompan=z='min(1.02,1+0.00005*on)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=125:s=1080x1920:fps=25",
                        '-frames:v','375','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(folder/'motion-preview.mp4')],check=True)
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir() if p.is_file() and p.name!='manifest.json'}
    (folder/'manifest.json').write_text(json.dumps(dict(company=job['company'],specimen=specimen,source_url=job['source_url'],order_id=job.get('order_id'),scope_sha256=job.get('scope_sha256'),files=files),indent=2))
    return dict(company=job['company'],files=len(files),proof_sha256=files['proof.pdf'])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('jobs',type=Path);p.add_argument('output',type=Path);p.add_argument('--no-video',action='store_true')
    p.add_argument('--commissioned-order');p.add_argument('--state',type=Path)
    a=p.parse_args()
    if a.output.resolve().is_relative_to(Path(__file__).resolve().parents[1]):raise ValueError('Private proof output must live outside public checkout')
    jobs=json.loads(a.jobs.read_text())
    if a.commissioned_order:
        from moneyfall.orders import Orders
        if not a.state or len(jobs)!=1 or a.no_video:raise ValueError('Commissioned rendering needs one paid order, private state and full video kit')
        db=Orders(a.state,repo=Path(__file__).resolve().parents[1])
        try:
            if not db.ready(a.commissioned_order):raise ValueError('Order needs confirmed payment and approved asset permissions')
            jobs[0]['specimen']=False
            order=db.get_order(a.commissioned_order)
            jobs[0]['order_id']=a.commissioned_order
            jobs[0]['scope_sha256']=hashlib.sha256(order['scope'].encode()).hexdigest()
        finally:db.close()
    for job in jobs:
        import re
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',job['slug']):raise ValueError('Unsafe output slug')
        if job.get('specimen') is False and not a.commissioned_order:raise ValueError('Client production requires an accepted paid order')
        print(json.dumps(render(job,a.output/job['slug'],video=not a.no_video)))
