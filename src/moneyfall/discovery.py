"""Company compatibility is evidence for review, never guaranteed money."""
import html
import ipaddress
import re
from html.parser import HTMLParser


def domain_name(value):
    if not isinstance(value,str):raise ValueError('Domain must be text')
    value=value.strip().lower()
    if value.startswith('www.'):value=value[4:]
    if not re.fullmatch(r'(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}',value):
        raise ValueError('Expected a public domain without path, port or credentials')
    if value.endswith(('.local','.localhost','.internal','.test','.invalid')):
        raise ValueError('Private/special-use domain is not a company website')
    return value


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip=0;self.in_title=False;self.text=[];self.title=[];self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style','noscript'):self.skip+=1
        if tag=='title':self.in_title=True
        if tag=='a':
            href=dict(attrs).get('href','')
            if href:self.links.append(href)
    def handle_endtag(self,tag):
        if tag in ('script','style','noscript'):self.skip=max(0,self.skip-1)
        if tag=='title':self.in_title=False
    def handle_data(self,data):
        if not self.skip:
            self.text.append(data)
            if self.in_title:self.title.append(data)


def extract_page(markup):
    p=PageParser();p.feed(markup)
    text=re.sub(r'\s+',' ',' '.join(p.text)).strip()
    emails=set(re.findall(r'(?<![\w.+-])[\w.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',text))
    emails.update(link[7:].split('?')[0] for link in p.links if link.startswith('mailto:'))
    return dict(title=' '.join(p.title).strip(),text=text[:100000],emails=sorted(emails),links=p.links[:300])


def classify(text):
    text=text.casefold()
    agency=any(k in text for k in ('marketing agency','digital marketing','advertising agency','creative agency','web design','marketing services'))
    content=any(k in text for k in ('content marketing','social media','video production','copywriting','graphic design'))
    local=any(k in text for k in ('hvac','roofing','roof replacement','plumbing','air conditioning repair'))
    unrelated=any(k in text for k in ('shoe store','product distribution','recruitment agency','job board'))
    if agency and content:route='white-label-content'
    elif local:route='local-creative'
    elif unrelated:route='reject'
    else:route='review'
    return dict(route=route,send_ready=False,
                basis='Public text suggests service fit; human evidence/contact/offer review still required',
                expected_revenue_cents=None)


def coverage(reported,companies):
    unique={domain_name(c['domain']) for c in companies if c.get('domain')}
    return dict(reported_matches=reported,captured=len(unique),
                capture_fraction=len(unique)/reported if reported else None,
                complete=bool(reported and len(unique)>=reported),
                qualified=0,paid=0,basis='Source-reported universe and deduplicated captured domains are different')
