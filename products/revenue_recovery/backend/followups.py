"""Reviewable, UNSENT template drafts. Never performs external communications."""
from __future__ import annotations
from collections.abc import Mapping
from .qualification import qualify_lead, validate_lead

MESSAGES = {
    "AC not cooling": "We can review the cooling concern and discuss possible next steps. We cannot confirm an appointment or repair timeline.",
    "heating issue": "We can review the heating concern and discuss possible next steps. We cannot confirm an appointment or repair timeline.",
    "repair": "We can review the repair request and clarify the work needed before discussing scheduling.",
    "estimate follow-up": "We can review the earlier estimate request and clarify any questions. No pricing or prior quote has been verified.",
    "AC maintenance": "We can discuss an AC maintenance request and possible appointment options.",
    "maintenance": "We can discuss a maintenance request and possible appointment options.",
}

def prepare_followup(lead: Mapping[str, object], *, opted_out: bool | None = None) -> dict[str, object]:
    """Fail closed on suppression; unknown consent produces an internal-only draft."""
    row = validate_lead(lead)
    q = qualify_lead(row, opted_out=opted_out)
    if q["decision"] == "suppressed":
        return {
            "schema_version": "rre-draft-v1", "synthetic": True,
            "external_ref": row["external_ref"], "status": "suppressed",
            "draft": None, "sent": False, "send_enabled": False,
            "requires_human_approval": True, "qualification": q,
            "idempotency_key": q["idempotency_key"] + ":suppressed",
        }
    body = ("Hello,\n\nRegarding synthetic reference " + row["external_ref"] +
            ": " + MESSAGES[row["need"]] +
            "\n\nThis is an internal synthetic preview only; consent, suppression, "
            "recipient identity, accuracy, and human approval must be verified before any external action.")
    return {
        "schema_version": "rre-draft-v1", "synthetic": True,
        "external_ref": row["external_ref"], "status": "pending_human_review",
        "draft": body, "sent": False, "send_enabled": False,
        "requires_human_approval": True, "qualification": q,
        "idempotency_key": q["idempotency_key"] + ":draft-v1",
    }
