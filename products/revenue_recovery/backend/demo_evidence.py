"""Read-only synthetic workflow scenarios with explicit evidence boundaries.

No customer records, real bookings, messages, payment receipts, API integrations,
or durable storage. Scenario stages are FIXTURES, not audited operational events.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from backend.qualification import validate_lead
from backend.ai_providers import get_provider

SCENARIOS = frozenset({"review", "appointment_mock", "closed_job_mock"})
STAGE_ORDER = (
    "inquiry_observed_synthetic",
    "qualification_reviewed_synthetic",
    "followup_drafted_unsent",
    "draft_reviewed_mock",
    "appointment_requested_mock",
    "appointment_confirmed_mock",
    "job_closed_mock",
)


def _event(reference: str, sequence: int, event_type: str, source: str) -> dict[str, Any]:
    """Stable evidence-labeled fixture, not a provider or payment record."""
    return {
        "synthetic": True,
        "event_id": f"{reference}:fixture:{sequence:02d}",
        "event_type": event_type,
        "sequence": sequence,
        "source": source,
        "source_evidence_verified": False,
        "operator_action_authenticated": False,
        "provider_receipt": None,
        "timestamp_verified": False,
        "external_side_effect": False,
    }


def simulate_evidence_path(lead: Mapping[str, object], scenario: str = "review") -> dict[str, Any]:
    """Build a deterministic, reviewable demonstration timeline.

    'closed_job_mock' does NOT imply a customer was contacted, an appointment
    was booked, a job was closed or money was collected. It is a narrative
    scenario for verifying that the attribution logic remains conservative.
    """
    if type(scenario) is not str or scenario not in SCENARIOS:
        raise ValueError("Unsupported synthetic scenario")
    row = validate_lead(lead)
    provider = get_provider("offline")
    if provider.uses_model is not False or provider.external_calls is not False:
        raise ValueError("Only the deterministic local provider is allowed")
    qualified = provider.qualify(row, opted_out=None)
    followup = provider.draft(row, opted_out=None)
    if qualified.get("outreach_allowed") is not False or followup.get("send_enabled") is not False:
        raise ValueError("Synthetic scenario cannot enable communications")
    if followup.get("sent") is not False or followup.get("status") != "pending_human_review":
        raise ValueError("Unexpected outbound draft state")
    count = {"review": 3, "appointment_mock": 6, "closed_job_mock": 7}[scenario]
    events = [
        _event(row["external_ref"], index + 1, kind, "local_synthetic_fixture")
        for index, kind in enumerate(STAGE_ORDER[:count])
    ]
    # Even mock-reviewed drafts are never enabled for external sending.
    return {
        "schema_version": "rre-demo-evidence-v1",
        "synthetic": True,
        "scenario": scenario,
        "external_ref": row["external_ref"],
        "source": "local_fixture_only",
        "events": events,
        "metrics": {
            "synthetic_inquiries": 1,
            "synthetic_review_drafts": 1,
            "mock_appointments": int(scenario in {"appointment_mock", "closed_job_mock"}),
            "mock_closed_jobs": int(scenario == "closed_job_mock"),
            "actual_messages_sent": 0,
            "actual_bookings_confirmed": 0,
            "actual_jobs_closed": 0,
            "verified_contractor_collections_cents": 0,
            "verified_recovered_revenue_cents": 0,
            "verified_rre_subscription_revenue_cents": 0,
            "verified_payment_receipts": 0,
        },
        "attribution": {
            "status": "unverifiable_synthetic_only",
            "claim": "No causal or financial attribution can be established from fixtures",
            "actual_provider_connection": False,
            "authenticated_payment_evidence": False,
            "double_counting_prohibited": True,
        },
        "gates": {
            "real_contact_consent": "unknown",
            "opt_out_status": "unknown",
            "human_approval_authenticated": False,
            "customer_identity_verified": False,
            "real_outreach_enabled": False,
            "payment_verification_enabled": False,
        },
    }


def aggregate_synthetic_scorecard(leads: list[Mapping[str, object]]) -> dict[str, Any]:
    """Safely aggregate *received* synthetic leads without inventing outcomes."""
    if type(leads) is not list:
        raise ValueError("Expected synthetic lead list")
    records = [validate_lead(lead) for lead in leads]
    refs = [str(row["external_ref"]) for row in records]
    if len(refs) != len(set(refs)):
        raise ValueError("Duplicate synthetic reference cannot be counted twice")
    return {
        "schema_version": "rre-demo-scorecard-v1",
        "synthetic": True,
        "source": "local_process_memory",
        "counts": {
            "received_demo_leads": len(records),
            "unreviewed_leads": len(records),
            "mock_confirmed_appointments": 0,
            "mock_closed_jobs": 0,
            "actual_bookings_confirmed": 0,
            "real_customers": None,  # Unconnected private subscription records are unknown
        },
        "verified": {
            "business_subscription_customers": 0,
            "rre_monthly_profit_cents": 0,
            "rre_subscription_revenue_cents": 0,
            "contractor_recovered_revenue_cents": 0,
            "payment_receipts": 0,
        },
        "limitations": [
            "This is a synthetic dashboard; no real CRM, calendar or bank is connected",
            "No outbound communications, customer consent or human identities verified",
            "Zero verified revenue is a lack of evidence, not a measured business result",
        ],
    }
