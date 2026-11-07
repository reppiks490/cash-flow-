"""Offline-only HVAC onboarding preview; never provisions a tenant or integration."""
from __future__ import annotations

from products.revenue_recovery.backend.onboarding import (
    OnboardingError, draft_subscription_quote, prepare_demo_workspace,
)

_ALLOWED = {"workspace", "monthly_price_usd", "crm_port", "email_port", "calendar_port"}
_PORTS = {"mock", "disabled"}


def preview_demo_onboarding(request: dict) -> dict:
    """Validate an exact synthetic-only contract and return an inert plan.

    No credentials, contact details, network access, persistence, invoices,
    appointments or outbound communication are accepted or produced.
    """
    if type(request) is not dict or set(request) != _ALLOWED:
        raise OnboardingError("Exact offline preview fields required")
    for name in ("crm_port", "email_port", "calendar_port"):
        if type(request[name]) is not str or request[name] not in _PORTS:
            raise OnboardingError(f"{name} must be mock or disabled")
    workspace = prepare_demo_workspace(request["workspace"])
    quote = draft_subscription_quote(request["monthly_price_usd"])
    return {
        "synthetic": True,
        "workspace_id": workspace.workspace_id,
        "industry": workspace.industry,
        "consent_mode": workspace.consent_mode,
        "ports": {name: request[name] for name in ("crm_port", "email_port", "calendar_port")},
        "quote": quote,
        "billing_status": "disabled",
        "outbound_enabled": False,
        "live_integrations_enabled": False,
        "tenant_provisioned": False,
        "pilot_authorized": False,
        "verified_customers": None,
        "verified_net_profit_usd": None,
    }
