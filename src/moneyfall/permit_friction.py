"""Source-backed municipal permit-friction research utilities.

This module deliberately separates public-record research from legal advice,
filing services, or claims of municipal approval. Scores are explicit heuristics
used to prioritize research markets; they are not legal/compliance risk scores.
"""

from __future__ import annotations

import math
from urllib.parse import urlparse


FACTORS = (
    "agency_handoffs",
    "sequential_dependencies",
    "manual_or_offline_steps",
    "inspection_dependencies",
    "deadline_pressure",
    "geographic_restrictions",
    "fee_complexity",
)

WEIGHTS = {
    "agency_handoffs": 0.15,
    "sequential_dependencies": 0.20,
    "manual_or_offline_steps": 0.15,
    "inspection_dependencies": 0.15,
    "deadline_pressure": 0.15,
    "geographic_restrictions": 0.10,
    "fee_complexity": 0.10,
}

VALID_REQUIREMENT_STATUSES = {"required", "may_require", "unknown"}


def _fraction(value):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 <= value <= 1
    ):
        raise ValueError("Permit-friction factors must be finite numbers from 0 to 1")
    return float(value)


def _score(value):
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 <= value <= 100
    ):
        raise ValueError("Permit-friction score must be a finite number from 0 to 100")
    return float(value)


def friction_score(profile):
    """Return a deterministic weighted friction score and explicit missing data.

    Missing or ``None`` factors fail closed: the market is unranked rather than
    silently receiving guessed values.
    """
    if not isinstance(profile, dict):
        raise ValueError("Permit-friction profile must be an object")
    missing = [factor for factor in FACTORS if profile.get(factor) is None]
    if missing:
        return {"score": 0, "tier": "unranked", "missing": missing}

    values = {factor: _fraction(profile[factor]) for factor in FACTORS}
    score = round(100 * sum(values[factor] * WEIGHTS[factor] for factor in FACTORS), 2)
    if score < 40:
        tier = "low"
    elif score < 60:
        tier = "moderate"
    elif score < 80:
        tier = "high"
    else:
        tier = "severe"
    return {"score": score, "tier": tier, "missing": []}


def offer_for_score(score):
    """Map friction to the smallest productized research scope worth testing."""
    score = _score(score)
    if score < 40:
        return {
            "action": "skip",
            "price_cents": 0,
            "scope": "Do not prospect this market until stronger friction evidence exists.",
        }
    if score < 60:
        return {
            "action": "single_city",
            "price_cents": 40000,
            "scope": "Single-City Permit Readiness Pack",
        }
    if score < 80:
        return {
            "action": "three_city",
            "price_cents": 80000,
            "scope": "Three-City Expansion Permit Map",
        }
    return {
        "action": "season_map",
        "price_cents": 160000,
        "scope": "Season / Multi-Jurisdiction Permit Readiness Map",
    }


def _official_source(url, official_domains):
    if not isinstance(url, str) or not url.startswith("https://"):
        return False
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")
    if host.endswith(".gov") or ".gov." in host:
        return True
    for domain in official_domains:
        normalized = str(domain).lower().strip().rstrip(".")
        if host == normalized or host.endswith("." + normalized):
            return True
    return False


def build_readiness_pack(municipality):
    """Normalize a municipality's reviewed requirements into a client-safe pack.

    Only official government sources (or an explicit official-domain allowlist)
    may support required/may-require/unknown classifications.
    """
    if not isinstance(municipality, dict) or not str(municipality.get("name", "")).strip():
        raise ValueError("Municipality name is required")
    if not str(municipality.get("retrieved_at", "")).strip():
        raise ValueError("retrieved_at is required")
    requirements = municipality.get("requirements")
    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list")
    official_domains = municipality.get("official_domains", [])
    if not isinstance(official_domains, list):
        raise ValueError("official_domains must be a list")

    grouped = {status: [] for status in VALID_REQUIREMENT_STATUSES}
    for item in requirements:
        if not isinstance(item, dict):
            raise ValueError("Each requirement must be an object")
        label = str(item.get("label", "")).strip()
        status = item.get("status")
        source_url = item.get("source_url")
        if not label or status not in VALID_REQUIREMENT_STATUSES:
            raise ValueError("Requirement label/status is invalid")
        if not _official_source(source_url, official_domains):
            raise ValueError("Requirements must be supported by an official HTTPS source")
        grouped[status].append({
            "label": label,
            "source_url": source_url,
            **({"note": str(item["note"]).strip()} if item.get("note") else {}),
        })

    return {
        "municipality": municipality["name"],
        "retrieved_at": municipality["retrieved_at"],
        "required": grouped["required"],
        "may_require": grouped["may_require"],
        "unknown": grouped["unknown"],
        "disclaimer": (
            "Research aid only; not legal advice, permit filing, municipal approval, "
            "or a guarantee that a vendor may operate. Requirements can change and "
            "must be confirmed with the issuing authority before relying on them."
        ),
    }
