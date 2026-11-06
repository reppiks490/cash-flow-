"""Synthetic-only onboarding and disabled billing contract for RRE.

No credentials, real customer details, money movement or external integrations.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


class OnboardingError(ValueError):
    """Invalid or unsafe onboarding data."""


@dataclass(frozen=True)
class DemoWorkspace:
    workspace_id: str
    industry: str
    synthetic: bool
    consent_mode: str
    billing_status: str = "disabled"


def prepare_demo_workspace(payload: dict) -> DemoWorkspace:
    """Accept strictly synthetic HVAC workspace metadata, never contact PII."""
    if not isinstance(payload, dict):
        raise OnboardingError("Expected object")
    expected = {"workspace_id", "industry", "synthetic", "consent_mode"}
    if set(payload) != expected:
        raise OnboardingError("Unexpected or missing fields; no live customer data allowed")
    if payload["synthetic"] is not True:
        raise OnboardingError("Only synthetic demo onboarding is enabled")
    if payload["industry"] != "hvac":
        raise OnboardingError("Only HVAC demo is supported")
    workspace_id = payload["workspace_id"]
    if not isinstance(workspace_id, str) or not workspace_id.startswith("demo-"):
        raise OnboardingError("workspace_id must start with demo-")
    if len(workspace_id) > 64 or not workspace_id[5:] or not all(
        c.isascii() and (c.isalnum() or c in "-_") for c in workspace_id
    ):
        raise OnboardingError("Invalid demo workspace ID")
    if payload["consent_mode"] != "manual_review_only":
        raise OnboardingError("Outbound communication must remain manual review only")
    return DemoWorkspace(workspace_id, "hvac", True, "manual_review_only")


def draft_subscription_quote(monthly_price_usd: str = "700.00") -> dict:
    """Create a nonbinding pricing hypothesis; never create a payment or invoice."""
    try:
        price = Decimal(monthly_price_usd)
    except (InvalidOperation, TypeError):
        raise OnboardingError("Invalid monthly price") from None
    if not price.is_finite() or price <= 0 or price.as_tuple().exponent < -2:
        raise OnboardingError("Price must be positive USD with <=2 decimal places")
    return {
        "synthetic": True,
        "nonbinding": True,
        "monthly_price_usd": str(price.quantize(Decimal("0.01"))),
        "billing_status": "disabled",
        "invoice_id": None,
        "payment_receipt": None,
        "send_enabled": False,
    }


def activate_billing(*_args, **_kwargs):
    """Explicitly deny all real billing while commercial release is gated."""
    raise PermissionError("Billing activation disabled pending owner approval and production controls")


def send_followup(*_args, **_kwargs):
    """Explicitly deny outbound messages in this prototype."""
    raise PermissionError("Outbound communications disabled pending approval and compliance review")
