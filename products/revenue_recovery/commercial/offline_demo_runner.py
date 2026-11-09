"""Executable, offline synthetic HVAC demo assertions; never a production gate.

Only deterministic pure product functions are invoked. This does not authenticate
a browser session, provider isolation, consent, customer outcomes, or receipts.
"""
from __future__ import annotations

from uuid import uuid4

from backend.consent_simulation import simulate_contact_policy
from backend.crm import preview_crm_envelope
from backend.demo_evidence import simulate_evidence_path
from backend.followups import prepare_followup
from backend.qualification import qualify_lead, validate_lead
from products.revenue_recovery.commercial.demo_trace_gate import (
    DemoEvidence, REQUIRED_STEPS, assess_demo_trace,
)

LEAD = {
    "synthetic": True, "external_ref": "DEMO-RRE-COMMERCIAL-1",
    "source": "website", "need": "repair", "status": "received",
}


def execute_offline_demo() -> dict:
    """Execute each assertion before recording a trace marker.

    Raises AssertionError/ValueError on failure; never catches an assertion to
    manufacture a passing marker. No client-supplied trace is accepted.
    """
    run_id = "local-" + uuid4().hex
    records = []

    def record(step: str, condition: bool) -> None:
        if not condition:
            raise AssertionError("Synthetic demo assertion failed: " + step)
        records.append(DemoEvidence(step, True, True, run_id))

    lead = validate_lead(LEAD)
    record("synthetic_intake", lead == LEAD and lead["synthetic"] is True)

    qualification = qualify_lead(lead)
    record("qualification_preview",
           qualification["synthetic"] is True
           and qualification["external_ref"] == lead["external_ref"]
           and qualification["outreach_allowed"] is False
           and bool(qualification["evidence"])
           and "contact_consent" in qualification["unknowns"])

    draft = prepare_followup(lead)
    record("unsent_followup_draft",
           draft["status"] == "pending_human_review"
           and bool(draft["draft"])
           and draft["sent"] is False
           and draft["send_enabled"] is False
           and draft["requires_human_approval"] is True)

    crm = preview_crm_envelope(lead)
    record("crm_dry_run",
           crm["synthetic"] is True and crm["dry_run"] is True
           and crm["transmitted"] is False
           and crm["provider_record_id"] is None
           and crm["appointment_confirmed"] is False)

    revoked = simulate_contact_policy(lead, "revoked_mock")
    record("consent_revocation_rejection",
           revoked["suppressed"] is True and revoked["draft"] is None
           and revoked["actual_message_sent"] is False
           and revoked["may_contact_real_person"] is False)

    evidence = simulate_evidence_path(lead, "closed_job_mock")
    metrics = evidence["metrics"]
    record("zero_verified_receipts",
           evidence["synthetic"] is True
           and evidence["attribution"]["authenticated_payment_evidence"] is False
           and metrics["verified_payment_receipts"] == 0
           and metrics["verified_rre_subscription_revenue_cents"] == 0
           and metrics["actual_messages_sent"] == 0
           and all(event["external_side_effect"] is False for event in evidence["events"]))

    if tuple(row.step for row in records) != REQUIRED_STEPS:
        raise AssertionError("Unexpected demo assertion order")
    result = assess_demo_trace(records)
    if result["synthetic_trace_shape_valid"] is not True:
        raise AssertionError("Synthetic trace rejected")
    return {"run_id": run_id, "asserted_steps": len(records), **result}
