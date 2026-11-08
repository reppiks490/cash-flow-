"""Fail-closed, synthetic-only commercial pilot readiness assessment.

No network, customer records, credentials, billing, or outbound effects.
"""
from __future__ import annotations

from dataclasses import dataclass

_REQUIRED = (
    "tenant_isolation", "private_storage", "consent_audit",
    "human_approval_audit", "suppression_enforcement", "qa_signoff",
    "legal_review", "owner_authorization", "provider_permissions",
)


@dataclass(frozen=True)
class PilotGateResult:
    synthetic: bool
    eligible_for_live_pilot: bool
    missing_controls: tuple[str, ...]
    classification: str


def assess_pilot_controls(evidence: dict) -> PilotGateResult:
    """Assess declarations, never convert declarations into real-world approval.

    Every control must be a literal boolean. A complete checklist still cannot
    authorize production or live data because no evidence is authenticated.
    """
    if type(evidence) is not dict or set(evidence) != set(_REQUIRED):
        raise ValueError("Expected exactly the approved control keys")
    if any(type(evidence[k]) is not bool for k in _REQUIRED):
        raise ValueError("Control values must be booleans")
    missing = tuple(k for k in _REQUIRED if not evidence[k])
    return PilotGateResult(
        synthetic=True,
        eligible_for_live_pilot=False,
        missing_controls=missing,
        classification="unverified_self_attestation" if not missing else "blocked",
    )
