"""Deterministic HVAC qualification; no network access or personal-data logging."""
from __future__ import annotations
from hashlib import sha256
import json
import re

URGENT = ("no heat", "no cooling", "no ac", "furnace stopped", "ac stopped", "heat stopped")
SERVICE = ("repair", "replace", "installation", "install", "maintenance", "service", "quote", "estimate", "broken", "not working")
OBJECTIONS = {"price": ("too expensive", "price", "cost", "budget"), "timing": ("next month", "later", "not ready"), "competitor": ("other contractor", "other quote", "competitor")}
OPT_OUT = ("unsubscribe", "stop contacting", "do not contact", "opt out", "remove me")

def _text(value):
    return value.strip().lower() if isinstance(value, str) else ""

def _contains_phrase(text: str, phrase: str) -> bool:
    """Match complete tokens/phrases, not substrings inside unrelated words."""
    return re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text) is not None

def qualify(lead: dict) -> dict:
    """Return explainable assessment. Caller must persist tenant-scoped dedup/idempotency."""
    if not isinstance(lead, dict):
        raise TypeError("lead must be a mapping")
    tenant = _text(lead.get("tenant_id"))
    source = _text(lead.get("source"))
    external_id = _text(lead.get("external_id"))
    if not tenant or not source or not external_id:
        raise ValueError("tenant_id, source and external_id are required")
    message = _text(lead.get("message"))[:10000]
    normalized = re.sub(r"\s+", " ", message)
    digest = sha256(json.dumps([tenant, source, external_id], separators=(",", ":")).encode()).hexdigest()
    evidence = []
    score = 0
    for label, words, points in (("urgent_hvac_need", URGENT, 50), ("service_intent", SERVICE, 35)):
        matches = [word for word in words if _contains_phrase(normalized, word)]
        if matches:
            score += points
            evidence.append({"rule": label, "source": "lead.message", "matched_terms": matches, "points": points})
    objections = [name for name, words in OBJECTIONS.items() if any(_contains_phrase(normalized, w) for w in words)]
    suppressed = bool(lead.get("opt_out") is True or any(_contains_phrase(normalized, w) for w in OPT_OUT))
    if suppressed:
        status = "suppressed"
    elif score >= 35:
        status = "qualified"
    else:
        status = "needs_review"
    return {
        "idempotency_key": digest, "status": status, "score": min(score, 100),
        "confidence": "rule_match" if evidence else "unknown",
        "unknowns": ["service_area", "availability", "contact_permission"],
        "evidence": evidence, "objections": objections, "opt_out": suppressed,
        "source": source, "external_id": external_id, "tenant_id": tenant,
        "synthetic": lead.get("synthetic") is True,
        "rubric_version": "hvac-v1",
    }
