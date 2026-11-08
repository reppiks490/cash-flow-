"""Fail-closed synthetic HVAC onboarding checklist; no external side effects."""
from __future__ import annotations

from dataclasses import dataclass

_ALLOWED = frozenset({
    "demo_workspace_created", "synthetic_fixture_loaded",
    "operator_review_walkthrough", "no_send_verified",
    "billing_disabled_verified", "crm_dry_run_verified",
})


@dataclass(frozen=True)
class OnboardingAssessment:
    synthetic: bool
    completed: tuple[str, ...]
    missing: tuple[str, ...]
    demo_ready: bool
    live_pilot_authorized: bool = False
    payment_enabled: bool = False
    outreach_enabled: bool = False


def assess_demo_onboarding(payload: object) -> OnboardingAssessment:
    """Validate strict boolean evidence markers; never grant production privileges.

    Checklist flags are unverified self-attestations, not proof of a control.
    """
    if type(payload) is not dict or set(payload) != _ALLOWED:
        raise ValueError("Expected exactly the six synthetic onboarding controls")
    if any(type(value) is not bool for value in payload.values()):
        raise ValueError("Controls must be strict booleans")
    completed = tuple(sorted(key for key in _ALLOWED if payload[key]))
    missing = tuple(sorted(_ALLOWED - set(completed)))
    return OnboardingAssessment(
        synthetic=True, completed=completed, missing=missing,
        demo_ready=not missing,
    )
