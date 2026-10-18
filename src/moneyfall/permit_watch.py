"""Zero-cost monitoring primitives for official municipal permit sources.

The watcher detects source changes; it never turns a changed webpage into a legal
conclusion. Changed/error sources require human review before downstream client
claims are refreshed.
"""

from __future__ import annotations

import hashlib
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class _VisibleHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._ignored = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript"}:
            self._ignored += 1

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript"} and self._ignored:
            self._ignored -= 1

    def handle_data(self, data):
        if not self._ignored:
            self.parts.append(data)


def host_allowed(host, allowed_domains):
    """Accept only an exact allowlisted hostname or one of its subdomains."""
    host = str(host or "").lower().strip().rstrip(".")
    if not host:
        return False
    for domain in allowed_domains or []:
        domain = str(domain or "").lower().strip().rstrip(".")
        if domain and (host == domain or host.endswith("." + domain)):
            return True
    return False


def catalog_urls(datasets):
    """Build a stable, deduplicated source catalog from permit-friction datasets.

    ``watch_exclusions`` is an explicit manual-review lane for official research
    pages that reject automated retrieval. An exclusion must still be an official
    HTTPS URL already present in ``source_urls``.
    """
    ordered = []
    index = {}
    for dataset in datasets:
        if not isinstance(dataset, dict):
            raise ValueError("Dataset must be an object")
        for market in dataset.get("municipalities", []):
            if not isinstance(market, dict):
                raise ValueError("Municipality entry must be an object")
            name = str(market.get("name", "")).strip()
            domains = [str(d).lower().strip().rstrip(".") for d in market.get("official_domains", []) if str(d).strip()]
            if not name or not domains:
                raise ValueError("Municipality name and official_domains are required")

            source_urls = [str(url) for url in market.get("source_urls", [])]
            exclusions = [str(url) for url in market.get("watch_exclusions", [])]
            for url in exclusions:
                parsed = urlparse(url)
                if url not in source_urls or parsed.scheme != "https" or not parsed.hostname or not host_allowed(parsed.hostname, domains):
                    raise ValueError(f"Invalid watch_exclusion for {name}: {url}")

            for url in source_urls:
                parsed = urlparse(url)
                if parsed.scheme != "https" or not parsed.hostname or not host_allowed(parsed.hostname, domains):
                    raise ValueError(f"Non-official or non-HTTPS permit source: {url}")
                if url in exclusions:
                    continue
                if url not in index:
                    entry = {"url": url, "markets": [name], "allowed_domains": list(domains)}
                    index[url] = entry
                    ordered.append(entry)
                else:
                    entry = index[url]
                    if name not in entry["markets"]:
                        entry["markets"].append(name)
                    for domain in domains:
                        if domain not in entry["allowed_domains"]:
                            entry["allowed_domains"].append(domain)
    return ordered


def fingerprint_content(content, content_type):
    """Hash normalized visible HTML text or raw non-HTML bytes."""
    if not isinstance(content, (bytes, bytearray)):
        raise ValueError("content must be bytes")
    content = bytes(content)
    kind = str(content_type or "").lower()
    if "html" in kind:
        parser = _VisibleHTML()
        parser.feed(content.decode("utf-8", errors="replace"))
        visible = " ".join(" ".join(parser.parts).split())
        payload = visible.encode("utf-8")
    else:
        payload = content
    return hashlib.sha256(payload).hexdigest()


def compare_snapshots(previous, current):
    """Classify each current URL as baseline, unchanged, changed, manual or error."""
    previous = previous or {}
    if not isinstance(previous, dict) or not isinstance(current, dict):
        raise ValueError("Snapshots must be objects")
    result = {}
    for url, observation in current.items():
        if not isinstance(observation, dict):
            raise ValueError("Snapshot observations must be objects")
        record = dict(observation)
        old_fingerprint = previous.get(url, {}).get("fingerprint") if isinstance(previous.get(url, {}), dict) else None
        if record.get("manual_only"):
            state = "error" if old_fingerprint else "manual"
            if state == "error" and not record.get("error"):
                record["error"] = "Previously monitorable official source now blocks automated retrieval"
        elif record.get("error"):
            state = "error"
        elif not old_fingerprint:
            state = "baseline"
        elif old_fingerprint == record.get("fingerprint"):
            state = "unchanged"
        else:
            state = "changed"
        record["state"] = state
        result[url] = record
    return result


def fetch_source(entry, *, timeout=20, max_bytes=2_000_000):
    """Fetch one allowlisted official source with redirect and size controls."""
    if not isinstance(entry, dict):
        raise ValueError("Catalog entry must be an object")
    url = str(entry.get("url", ""))
    allowed = entry.get("allowed_domains", [])
    parsed = urlparse(url)
    if parsed.scheme != "https" or not host_allowed(parsed.hostname, allowed):
        raise ValueError("Source URL must be allowlisted HTTPS")
    req = Request(url, headers={"User-Agent": "MONEYFALL-PermitSourceWatch/1.0 (+source-change-monitor)"})
    with urlopen(req, timeout=timeout) as response:
        final_url = response.geturl()
        final_host = urlparse(final_url).hostname
        if not host_allowed(final_host, allowed):
            raise ValueError("Redirect left official source allowlist")
        content_type = response.headers.get("Content-Type", "application/octet-stream").split(";", 1)[0].strip().lower()
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError("Permit source exceeds maximum monitored size")
        status = getattr(response, "status", 200)
        return {
            "fingerprint": fingerprint_content(body, content_type),
            "status_code": int(status),
            "content_type": content_type,
            "final_url": final_url,
            "bytes": len(body),
            "markets": list(entry.get("markets", [])),
        }


def scan_sources(catalog):
    """Fetch every source, retaining failures and access blocks as explicit state."""
    current = {}
    for entry in catalog:
        url = entry["url"]
        try:
            current[url] = fetch_source(entry)
        except HTTPError as exc:
            if exc.code == 403:
                current[url] = {
                    "manual_only": True,
                    "status_code": 403,
                    "reason": "Official source denies automated retrieval; review manually without bypassing access controls",
                    "markets": list(entry.get("markets", [])),
                }
            else:
                current[url] = {"error": f"HTTPError: HTTP Error {exc.code}: {exc.reason}", "markets": list(entry.get("markets", []))}
        except Exception as exc:  # network/provider failures are reportable state
            current[url] = {"error": f"{type(exc).__name__}: {exc}", "markets": list(entry.get("markets", []))}
    return current
