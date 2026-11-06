"""Side-effect-free HVAC onboarding plan for synthetic demonstrations.

This is a plan builder, NOT a connected CRM, calendar, email or billing port.
It accepts only enumerated mock/disabled adapters and never receives secrets,
contact details, customer records or a send/charge authorization.
"""
from __future__ import annotations

from backend.onboarding import OnboardingError
from commercial.demo_readiness import preview_demo_offer

_ALLOWED_PORTS = frozenset(("disabled", "mock"))


def build_offline_pilot_plan(
    workspace: dict,
    checks: dict,
    *,
    crm_port: str = "mock",
    email_port: str = "mock",
    calendar_port: str = "mock",
    monthly_price_usd: str = "700.00",
) -> dict:
    """Produce a reviewable synthetic demo setup with every live operation denied.

    The 'mock' choice only enables an offline PREVIEW path for a later adapter;
    no CRM/email/calendar service is connected, instantiated or invoked.
    """
    selected = {"crm": crm_port, "email": email_port, "calendar": calendar_port}
    for name, value in selected.items():
        if type(value) is not str or value not in _ALLOWED_PORTS:
            raise OnboardingError(f"{name}_port must be 'disabled' or 'mock'")

    offer = preview_demo_offer(workspace, checks, monthly_price_usd)
    integrations = {
        name: {
            "port": value,
            "preview_available": value == "mock",
            "connected": False,
            "live_read_enabled": False,
            "live_write_enabled": False,
        }
        for name, value in selected.items()
    }
    return {
        "schema": "rre.synthetic_offline_pilot_plan.v1",
        "workspace_id": offer["workspace_id"],
        "industry": "hvac",
        "synthetic": True,
        "stage": "offline_demonstration_only",
        "demo_readiness": offer["readiness"],
        "missing_checks": offer["missing_checks"],
        "human_review_required": True,
        "pilot_ready": False,
        "live_customer_onboarding_enabled": False,
        "outreach_enabled": False,
        "calendar_booking_enabled": False,
        "crm_writes_enabled": False,
        "billing_enabled": False,
        "integrations": integrations,
        "quote": offer["quote"],
        "verified_customer_count": None,
        "verified_receipts_usd": None,
        "verified_monthly_net_profit_usd": None,
        "unverified_price_hypothesis": True,
    }
