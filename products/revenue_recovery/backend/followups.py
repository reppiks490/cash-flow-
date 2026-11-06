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

OBJECTION_TEMPLATES = {
    "price": "We can review pricing questions related to the HVAC request; no price, discount, or prior quote is verified.",
    "timing": "We can discuss timing concerns without promising scheduling, technician availability, or a completion date.",
    "competitor": "We understand you may be comparing providers; we can clarify the HVAC scope without claims about other contractors.",
}


def prepare_followup(lead: Mapping[str, object], *, opted_out: bool | None = None,
                     objection: str | None = None) -> dict[str, object]:
    """Fail closed on suppression; unknown consent produces an internal-only draft."""
    row = validate_lead(lead)
    if objection is not None and (type(objection) is not str or objection not in OBJECTION_TEMPLATES):
        raise ValueError("objection must be an approved synthetic category or None")
    q = qualify_lead(row, opted_out=opted_out)
    meta = ({"objection_category": objection, "objection_source": "unverified_caller_supplied_synthetic_enum"}
            if objection is not None else {})
    if q["decision"] == "suppressed":
        return {
            "schema_version": "rre-draft-v1", "synthetic": True,
            "external_ref": row["external_ref"], "status": "suppressed",
            "draft": None, "sent": False, "send_enabled": False,
            "requires_human_approval": True, "qualification": q,
            "idempotency_key": q["idempotency_key"] + ":suppressed" +
                               (":objection-" + objection if objection is not None else ""),
            **meta,
        }
    body = ("Hello,\n\nRegarding synthetic reference " + row["external_ref"] +
            ": " + MESSAGES[row["need"]] +
            (" " + OBJECTION_TEMPLATES[objection] if objection is not None else "") +
            "\n\nThis is an internal synthetic preview only; consent, suppression, "
            "recipient identity, accuracy, and human approval must be verified before any external action.")
    return {
        "schema_version": "rre-draft-v1", "synthetic": True,
        "external_ref": row["external_ref"], "status": "pending_human_review",
        "draft": body, "sent": False, "send_enabled": False,
        "requires_human_approval": True, "qualification": q,
        "idempotency_key": q["idempotency_key"] + ":draft-v1" +
                           (":objection-" + objection if objection is not None else ""),
        **meta,
    }


def recheck_followup_for_review(
    lead: Mapping[str, object],
    prior: Mapping[str, object],
    *,
    opted_out: bool | None,
) -> dict[str, object]:
    """Refresh a synthetic cached draft before another human review.

    Never trusts or republishes prior draft text. Validates the entire cached
    snapshot against current deterministic rules, then recomputes using the
    caller's current *mock* opt-out fixture. No real consent check, approval,
    persistence, recipient lookup, model call or communication occurs.
    """
    row = validate_lead(lead)
    if not isinstance(prior, Mapping):
        raise ValueError("Prior synthetic draft must be a mapping")
    prior_qualification = prior.get("qualification")
    if not isinstance(prior_qualification, Mapping):
        raise ValueError("Prior draft qualification is missing")
    previous_objection = prior.get("objection_category")
    previous_flag = prior_qualification.get("opted_out")
    expected_prior = prepare_followup(
        row, opted_out=previous_flag, objection=previous_objection
    )
    if dict(prior) != expected_prior:
        raise ValueError("Cached synthetic draft does not match trusted offline rules")
    refreshed = prepare_followup(
        row, opted_out=opted_out, objection=previous_objection
    )
    return {
        "schema_version": "rre-review-recheck-v1",
        "synthetic": True,
        "external_ref": row["external_ref"],
        "review_status": (
            "suppressed" if refreshed["status"] == "suppressed"
            else "fresh_human_review_required"
        ),
        "replay_changed": (
            expected_prior["idempotency_key"] != refreshed["idempotency_key"]
        ),
        "outreach_enabled": False,
        "sent": False,
        "requires_human_approval": True,
        "followup": refreshed,
    }
