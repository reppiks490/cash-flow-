"""Human-review-only HVAC follow-up drafting. No sending or provider calls."""
from __future__ import annotations
from hashlib import sha256
import json

def draft_followup(assessment: dict, *, approved_contact: bool = False) -> dict:
    if assessment.get("opt_out") or assessment.get("status") == "suppressed":
        return {"status": "blocked", "reason": "opt_out", "draft": None}
    if assessment.get("status") != "qualified":
        return {"status": "blocked", "reason": "not_qualified", "draft": None}
    if not approved_contact:
        return {"status": "blocked", "reason": "contact_permission_unverified", "draft": None}
    objections = assessment.get("objections") or []
    if "price" in objections:
        body = "Thanks for your HVAC inquiry. We can discuss the scope and provide an estimate for your review. Would you like to arrange a time?"
    elif "timing" in objections:
        body = "Thanks for your HVAC inquiry. We understand timing may be flexible. Would you prefer to discuss options now or at a later date?"
    else:
        body = "Thanks for your HVAC inquiry. Would you like to schedule a conversation about the service you need?"
    key = sha256(json.dumps([assessment.get("idempotency_key"), "hvac-followup-v1"], separators=(",", ":")).encode()).hexdigest()
    return {"status": "pending_human_review", "draft_id": key, "draft": body,
            "auto_send": False, "approved": False, "channel": "unspecified",
            "requires": ["human_approval", "current_consent_check", "suppression_recheck"],
            "template_version": "hvac-followup-v1"}
