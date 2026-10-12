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
    lines=[];line=''
    for word in text.split():
        candidate=(line+' '+word).strip()
        if font.getlength(candidate)>width and line:lines.append(line);line=word
        else:line=candidate
    if line:lines.append(line)
    return lines


def render_card(card,index,folder,accent,*,specimen=True):
    width,height=1080,1920
    image=Image.new('RGB',(width,height),'#101a23');draw=ImageDraw.Draw(image)
    for y in range(0,height,80):draw.line((0,y,width,y),fill='#14232e',width=1)
    draw.rounded_rectangle((70,80,1010,1840),radius=40,outline='#2b414e',width=2)
    draw.rectangle((100,142,260,154),fill=accent)
    tiny=ImageFont.truetype(str(FONT),28)
    small=ImageFont.truetype(str(FONT),39)
    titlefont=ImageFont.truetype(str(BOLD),91)
    bodyfont=ImageFont.truetype(str(FONT),47)
    label='ORIGINAL SPEC CONCEPT' if specimen else 'APPROVED CLIENT CONCEPT'
    footer='UNCOMMISSIONED SAMPLE / NO RESULTS CLAIMED' if specimen else 'CLIENT CONTENT KIT / REVIEW BEFORE PUBLISHING'
    draw.text((100,194),label,font=tiny,fill='#9fb5c2')
    draw.text((100,306),f'0{index} / CONTENT PILOT',font=small,fill=accent)
    y=500
    titles=wrap(card['headline'],titlefont,870)
    if len(titles)>5:raise ValueError('Headline is too long for portrait card')
    for line in titles:draw.text((100,y),line,font=titlefont,fill='#f3f8fa');y+=116
    y=max(1130,y+80)
    bodies=wrap(card['body'],bodyfont,850)
    if y+len(bodies)*64>1540:raise ValueError('Body is too long for portrait card')
    for line in bodies:draw.text((100,y),line,font=bodyfont,fill='#b8cbd6');y+=64
    draw.rounded_rectangle((100,1580,980,1690),radius=18,fill=accent)
    ctafont=ImageFont.truetype(str(BOLD),37)
    if ctafont.getlength(card['cta'])>820:raise ValueError('CTA is too long')
    draw.text((130,1610),card['cta'],font=ctafont,fill='#101a23')
    draw.text((100,1754),footer,font=tiny,fill='#8ea6b4')
    png=folder/f'card-{index:03}.png';image.save(png)
    # Same editable text and composition in SVG.
    lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1920" viewBox="0 0 1080 1920">',
           '<rect width="1080" height="1920" fill="#101a23"/>',
           f'<rect x="100" y="142" width="160" height="12" fill="{accent}"/>',
           f'<text x="100" y="225" fill="#9fb5c2" font-family="DejaVu Sans, sans-serif" font-size="28">{label}</text>']
    for n,line in enumerate(titles):lines.append(f'<text x="100" y="{590+n*116}" fill="#f3f8fa" font-family="DejaVu Sans, sans-serif" font-weight="bold" font-size="91">{html.escape(line)}</text>')
    for n,line in enumerate(bodies):lines.append(f'<text x="100" y="{max(1130,500+len(titles)*116+80)+45+n*64}" fill="#b8cbd6" font-family="DejaVu Sans, sans-serif" font-size="47">{html.escape(line)}</text>')
    lines.extend([f'<rect x="100" y="1580" width="880" height="110" rx="18" fill="{accent}"/>',
                  f'<text x="130" y="1650" fill="#101a23" font-family="DejaVu Sans, sans-serif" font-weight="bold" font-size="37">{html.escape(card["cta"])}</text>',
                  f'<text x="100" y="1782" fill="#8ea6b4" font-family="DejaVu Sans, sans-serif" font-size="28">{footer}</text></svg>'])
    (folder/f'card-{index:03}.svg').write_text('\n'.join(lines))
    return png


def pdf(job,images,path):
    c=canvas.Canvas(str(path),pagesize=(612,792));c.setTitle('Original content pilot - '+job['company'])
    c.setFillColor(HexColor('#101a23'));c.rect(0,0,612,792,fill=1,stroke=0)
    c.setFillColor(HexColor(job['accent']));c.setFont('Helvetica-Bold',10)
    specimen=job.get('specimen',True)
    c.drawString(40,752,'MONEYFALL / ORIGINAL SPECIMEN' if specimen else 'MONEYFALL / CLIENT CONTENT KIT')
    c.setFillColor(HexColor('#f3f8fa'));c.setFont('Helvetica-Bold',22)
    c.drawString(40,710,job['company'][:43])
    c.setFont('Helvetica',10);c.setFillColor(HexColor('#b8cbd6'))
    for n,line in enumerate(wrap(job['observed'],ImageFont.truetype(str(FONT),10),520)):
        c.drawString(40,682-14*n,line)
    for i,image in enumerate(images):c.drawImage(ImageReader(image),40+i*178,335,width=166,height=295,mask='auto')
    c.setFont('Helvetica-Bold',14);c.setFillColor(HexColor('#f3f8fa'));c.drawString(40,296,'A $149 white-label content pilot')
    c.setFont('Helvetica',10);c.setFillColor(HexColor('#b8cbd6'))
    scope=['3 portrait graphics + editable SVGs; 1 caption-led 15-second motion preview.',
           '3 captions and CTA options; one revision; no subscription or ad spend.',
           '48-hour delivery after accepted brief, payment and approved brand assets.',
           'Spec work only. No claimed client relationship, leads or revenue outcomes.' if specimen else 'Commissioned content kit. Review approved brand claims before publishing.',
           'Filming, voiceover, account access and publishing are outside this scope.']
    for i,line in enumerate(scope):c.drawString(40,273-i*17,line)
    c.setFont('Helvetica-Bold',10);c.drawString(40,150,'Why this concept fits')
    c.setFont('Helvetica',9)
    for n,line in enumerate(wrap(job['hypothesis'],ImageFont.truetype(str(FONT),9),520)):
        c.drawString(40,133-13*n,line)
    c.setFillColor(HexColor('#8ea6b4'));c.setFont('Helvetica',7)
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
