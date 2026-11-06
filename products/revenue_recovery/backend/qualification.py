"""Deterministic, explainable HVAC qualification for synthetic-only demo leads.

This is a rule engine, not an LLM or a claim of model-derived confidence.
"""
from __future__ import annotations
import hashlib
import json
from collections.abc import Mapping
from backend.contracts import SOURCES, NEEDS, REF

RUBRIC_VERSION = "hvac-demo-v1"
RULES = {
    "AC not cooling": ("urgent_service", 90, "cooling_failure"),
    "heating issue": ("urgent_service", 90, "heating_failure"),
    "repair": ("service", 75, "repair_request"),
    "estimate follow-up": ("estimate_follow_up", 80, "estimate_follow_up"),
    "AC maintenance": ("maintenance", 65, "maintenance_request"),
    "maintenance": ("maintenance", 65, "maintenance_request"),
}

def validate_lead(lead: Mapping[str, object]) -> dict[str, object]:
    """Accept only the shared synthetic v0.1a lead contract.

    DEMO/QA prefixes do not prove a value is free of personal information.
    Real customer data must not enter this untrusted synthetic demo.
    """
    if not isinstance(lead, Mapping):
        raise ValueError("Lead must be a mapping")
    if set(lead) != {"synthetic", "external_ref", "source", "need", "status"}:
        raise ValueError("Expected exact synthetic v0.1a stored lead fields")
    if lead["synthetic"] is not True or lead["status"] != "received":
        raise ValueError("Only received synthetic demo leads supported")
    ref, source, need = lead["external_ref"], lead["source"], lead["need"]
    if not isinstance(ref, str) or not REF.fullmatch(ref):
        raise ValueError("Invalid synthetic reference")
    if not isinstance(source, str) or source not in SOURCES:
        raise ValueError("Invalid source category")
    if not isinstance(need, str) or need not in NEEDS:
        raise ValueError("Invalid need category")
    return dict(lead)

def qualify_lead(lead: Mapping[str, object], *, opted_out: bool | None = None) -> dict[str, object]:
    """Return a reproducible decision; unknown consent never permits outreach.

    opted_out=None means suppression status has not been checked, NOT consent.
    """
    row = validate_lead(lead)
    if opted_out is not None and type(opted_out) is not bool:
        raise ValueError("opted_out must be true, false, or unknown")
    category, priority, rule = RULES[row["need"]]
    suppressed = opted_out is True
    # Key replay identity to all validated lead fields; the HTTP store separately
    # rejects conflicting references. Caller-supplied suppression fixtures
    # (unknown/false/true) must not share replay identity across revocations.
    # These flags are NOT evidence of lawful real-world consent.
    fingerprint = hashlib.sha256(json.dumps(
        [RUBRIC_VERSION, row["external_ref"], row["source"], row["need"], opted_out],
        separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")).hexdigest()
    return {
        "schema_version": "rre-qualification-v1",
        "rubric_version": RUBRIC_VERSION,
        "synthetic": True,
        "external_ref": row["external_ref"],
        "decision": "suppressed" if suppressed else "qualified_for_human_review",
        "category": category,
        "priority_score": priority,
        "confidence": None,
        "confidence_kind": "not_model_calibrated",
        "unknowns": ["contact_consent", "identity", "service_area", "availability", "pricing", "real_inquiry_provenance"] + (["suppression_status"] if opted_out is None else []),
        "evidence": [
            {"field": "need", "value": row["need"], "rule": rule, "provenance": "synthetic_intake"},
            {"field": "source", "value": row["source"], "rule": "accepted_source_category", "provenance": "synthetic_intake"},
        ],
        "outreach_allowed": False,
        "opted_out": opted_out,
        "idempotency_key": f"{RUBRIC_VERSION}:{fingerprint}",
    }
