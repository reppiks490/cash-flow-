"""Fail-closed mock consent and opt-out exercise.

This is deliberately NOT a legal compliance engine or a communications
authorization. It handles no recipient/contact data and cannot send messages.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.ai_providers import get_provider
from backend.qualification import validate_lead

POLICY_SCENARIOS = frozenset({"unknown", "revoked_mock", "consent_record_mock"})


def simulate_contact_policy(lead: Mapping[str, object], mode: str = "unknown") -> dict[str, Any]:
    """Demonstrate a suppression policy without granting real consent."""
    if type(mode) is not str or mode not in POLICY_SCENARIOS:
        raise ValueError("Unsupported local policy fixture")
    row = validate_lead(lead)
    opted_out = True if mode == "revoked_mock" else (False if mode == "consent_record_mock" else None)
    provider = get_provider("offline")
    if provider.uses_model is not False or provider.external_calls is not False:
        raise ValueError("External model cannot authorize simulated communication")
    qualification = provider.qualify(row, opted_out=opted_out)
    draft = provider.draft(row, opted_out=opted_out)
    suppressed = mode == "revoked_mock"
    if draft.get("sent") is not False or draft.get("send_enabled") is not False:
        raise ValueError("Unsafe provider returned send-enabled draft")
    if qualification.get("outreach_allowed") is not False:
        raise ValueError("Unsafe provider returned outreach authorization")
    if suppressed and (draft.get("draft") is not None or draft.get("status") != "suppressed"):
        raise ValueError("Revoked fixture must not produce a draft")
    if not suppressed and draft.get("status") != "pending_human_review":
        raise ValueError("Nonsuppressed fixture still requires human review")
    reason_codes = ["prototype_transport_disabled", "operator_identity_unverified",
                    "consent_evidence_unverified", "no_real_contact_source"]
    if suppressed:
        reason_codes.insert(0, "synthetic_opt_out_revocation")
    elif mode == "unknown":
        reason_codes.insert(0, "consent_and_suppression_unknown")
    else:
        reason_codes.insert(0, "mock_consent_record_not_verified")
    return {
        "schema_version": "rre-demo-consent-v1",
        "synthetic": True,
        "external_ref": row["external_ref"],
        "mode": mode,
        "suppressed": suppressed,
        "consent_verified": False,
        "operator_authorized": False,
        "may_contact_real_person": False,
        "recipient_address": None,
        "actual_message_sent": False,
        "review_required": True,
        "reasons": reason_codes,
        "draft": None if suppressed else draft["draft"],
        "draft_status": draft["status"],
        "provider": provider.provider_id,
    }
