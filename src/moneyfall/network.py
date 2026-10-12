"""Bounded public HTTPS reads with DNS pinning and same-domain redirects."""
import http.client
import ipaddress
import socket
import ssl
from urllib.parse import urlparse,urljoin
from .discovery import domain_name

AGENT='MoneyfallResearch/0.2'


def public_address(ip):
    try:return ipaddress.ip_address(ip).is_global
    except ValueError:return False


class PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self,host,address,timeout):
        super().__init__(host,timeout=timeout,context=ssl.create_default_context())
        self.address=address
    def connect(self):
        sock=socket.create_connection((self.address,443),self.timeout)
        self.sock=self._context.wrap_socket(sock,server_hostname=self.host)


def fetch_public(url,*,timeout=12,limit=2_000_000,redirects=3):
    original=urlparse(url)
    root=domain_name(original.hostname or '')
    for _ in range(redirects+1):
        p=urlparse(url)
        if p.scheme!='https' or p.username or p.password or p.port not in (None,443) or domain_name(p.hostname or '')!=root:
            raise ValueError('Only same-company public HTTPS URLs on port 443 are allowed')
        addresses={item[4][0] for item in socket.getaddrinfo(p.hostname,443,type=socket.SOCK_STREAM)}
        if not addresses or any(not public_address(ip) for ip in addresses):raise ValueError('Nonpublic DNS resolution blocked')
        address=sorted(addresses,key=lambda ip:(':' in ip,ip))[0]
        conn=PinnedHTTPS(p.hostname,address,timeout)
        try:
            conn.request('GET',p.path or '/',headers={'User-Agent':AGENT,'Accept':'text/html,text/plain','Accept-Encoding':'identity'})
            response=conn.getresponse()
            if response.status in (301,302,303,307,308):
                location=response.getheader('Location')
                if not location:raise ValueError('Redirect missing destination')
                url=urljoin(url,location);continue
            if response.status!=200:raise ValueError(f'Public website HTTP {response.status}')
            raw=response.read(limit+1)
            if len(raw)>limit:raise ValueError('Public response exceeds size limit')
            return dict(url=url,text=raw.decode('utf-8',errors='replace'),content_type=response.getheader('Content-Type',''))
        finally:conn.close()
    raise ValueError('Too many website redirects')
