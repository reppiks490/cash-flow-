"""Fail-closed, offline evidence gate for an HVAC synthetic demo run.

This checks an in-memory trace shape, not external execution, customer consent,
operator authority, payment receipts, or production/pilot readiness.
"""
from dataclasses import dataclass

REQUIRED_STEPS = (
    "synthetic_intake",
    "qualification_preview",
    "unsent_followup_draft",
    "crm_dry_run",
    "consent_revocation_rejection",
    "zero_verified_receipts",
)


@dataclass(frozen=True)
class DemoEvidence:
    """Caller-supplied synthetic trace marker; not authenticated execution evidence.

    The caller controls every field, including ``passed`` and ``run_id``.
    Validation only checks the shape and consistency of these assertions.
    """
    step: str
    passed: bool
    synthetic: bool
    run_id: str


def assess_demo_trace(records: object) -> dict:
    """Reject partial, malformed, mixed-run or non-synthetic evidence.

    A passing result means only that caller-provided local trace records have
    the expected shape. It cannot authenticate a real test run.
    """
    if type(records) not in (tuple, list):
        raise ValueError("Trace must be a list or tuple")
    if len(records) != len(REQUIRED_STEPS):
        return _decision("Missing or extra demo steps")
    seen = set()
    run_ids = set()
    for record in records:
        if type(record) is not DemoEvidence:
            raise ValueError("Invalid demo evidence record")
        if type(record.step) is not str or record.step not in REQUIRED_STEPS:
            raise ValueError("Unknown demo step")
        if record.step in seen:
            return _decision("Duplicate demo step")
        seen.add(record.step)
        if type(record.passed) is not bool or type(record.synthetic) is not bool:
            raise ValueError("Demo flags must be exact booleans")
        if type(record.run_id) is not str or not (1 <= len(record.run_id) <= 64):
            raise ValueError("Invalid local run identifier")
        if not all(c.isascii() and (c.isalnum() or c in "-_") for c in record.run_id):
            raise ValueError("Invalid local run identifier")
        run_ids.add(record.run_id)
        if not record.passed or not record.synthetic:
            return _decision("Step failed or not explicitly synthetic")
    if seen != set(REQUIRED_STEPS) or len(run_ids) != 1:
        return _decision("Incomplete or mixed-run demo trace")
    return _decision("All expected synthetic trace markers present", valid=True)


def _decision(reason: str, valid: bool = False) -> dict:
    return {
        "synthetic_trace_shape_valid": valid,
        "execution_independently_verified": False,
        "pilot_ready": False,
        "outreach_authorized": False,
        "billing_authorized": False,
        "verified_revenue_cents": None,
        "reason": reason,
    }
