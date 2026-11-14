"""Fail-closed, synthetic-only HVAC pilot readiness assessment.

This is a local planning aid, not an authorization, customer onboarding,
security certification, or production release decision.
"""
from __future__ import annotations

REQUIRED_GATES = (
    "tenant_security_reviewed",
    "consent_and_suppression_reviewed",
    "retention_and_deletion_reviewed",
    "operator_approval_workflow_reviewed",
    "qa_signoff_recorded",
    "owner_release_approval_recorded",
)
EXPECTED = frozenset({"synthetic", "industry", *REQUIRED_GATES})


class ReadinessError(ValueError):
    """Unsupported readiness payload."""


def assess_demo_pilot_readiness(payload: dict) -> dict:
    """Evaluate boolean checklist without accepting names, secrets or free text.

    Even all-green checklist values do not authorize external activity:
    evidence must be independently verified outside this synthetic prototype.
    """
    if type(payload) is not dict or set(payload) != EXPECTED:
        raise ReadinessError("Expected only the fixed synthetic readiness fields")
    if payload["synthetic"] is not True or payload["industry"] != "hvac":
        raise ReadinessError("Only synthetic HVAC readiness is supported")
    if any(type(payload[k]) is not bool for k in REQUIRED_GATES):
        raise ReadinessError("Readiness gates must be exact booleans")
    missing = [k for k in REQUIRED_GATES if not payload[k]]
    return {
        "classification": "synthetic_self_attestation_only",
        "synthetic": True,
        "checklist_complete": not missing,
        "unmet_checklist_gates": missing,
        "pilot_authorized": False,
        "production_ready": False,
        "outreach_enabled": False,
        "billing_enabled": False,
        "provider_connections_enabled": False,
        "independent_evidence_verified": False,
    }
