"""Offline, synthetic-only HVAC demo onboarding readiness checks.

No network, persistence, customer data, billing, or outbound side effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from backend.onboarding import OnboardingError, prepare_demo_workspace, draft_subscription_quote

REQUIRED_CHECKS = (
    "synthetic_fixture_reviewed",
    "operator_demo_walkthrough_reviewed",
    "human_approval_policy_reviewed",
    "no_live_credentials_confirmed",
    "no_customer_data_confirmed",
)


@dataclass(frozen=True)
class DemoReadiness:
    workspace_id: str
    synthetic: bool
    status: str
    missing_checks: tuple[str, ...]
    billing_enabled: bool = False
    outreach_enabled: bool = False
    crm_writes_enabled: bool = False


def evaluate_demo_readiness(workspace: Mapping[str, object], checks: Mapping[str, object]) -> DemoReadiness:
    """Validate a demo request, never authorize production operations.

    All checklist entries must be literal booleans. Missing/false entries block
    even offline demo readiness. A ready demo still cannot contact anyone.
    """
    demo = prepare_demo_workspace(workspace)
    if not isinstance(checks, dict) or set(checks) != set(REQUIRED_CHECKS):
        raise OnboardingError("Checklist must contain exactly the documented checks")
    if any(type(value) is not bool for value in checks.values()):
        raise OnboardingError("Checklist values must be literal booleans")
    missing = tuple(key for key in REQUIRED_CHECKS if not checks[key])
    return DemoReadiness(
        workspace_id=demo.workspace_id,
        synthetic=True,
        status="blocked" if missing else "offline_demo_ready",
        missing_checks=missing,
    )


def preview_demo_offer(workspace: Mapping[str, object], checks: Mapping[str, object],
                       monthly_price_usd: str = "700.00") -> dict:
    """Side-effect-free quote with a fail-closed readiness result."""
    readiness = evaluate_demo_readiness(workspace, checks)
    quote = draft_subscription_quote(monthly_price_usd)
    return {
        "workspace_id": readiness.workspace_id,
        "readiness": readiness.status,
        "missing_checks": list(readiness.missing_checks),
        "synthetic": True,
        "nonbinding": True,
        "billing_enabled": False,
        "outreach_enabled": False,
        "crm_writes_enabled": False,
        "quote": quote,
    }
