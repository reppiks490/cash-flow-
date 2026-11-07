"""Offline, fail-closed acceptance evidence for synthetic HVAC demo rehearsals.

No network, customer records, real credentials, payments, or outbound operations.
This classifies self-reported synthetic rehearsal data; a matching commit SHA\nDOES NOT authenticate any test execution. Never emit a verified PASS.\nNOT production authorization.
"""
from __future__ import annotations

import re
from collections.abc import Mapping

CHECKS = (
    "intake_dedupe",
    "qualification_provenance",
    "draft_unsent",
    "consent_suppression",
    "crm_calendar_mock",
    "receipt_disclosure",
    "billing_outbound_disabled",
)
STATUSES = frozenset(("PASS", "FAIL", "NOT_RUN"))
SHA = re.compile(r"[0-9a-f]{40}\Z")


def evaluate_demo_evidence(record: Mapping[str, object]) -> dict[str, object]:
    """Validate exact closed schema; never infer success from missing evidence.

    Each check requires a status and a synthetic-only, non-PII evidence reference
    (a 40-character Git SHA for PASS; no URL, names, or free-text notes).
    """
    if not isinstance(record, Mapping) or set(record) != {"synthetic", "commit", "checks"}:
        raise ValueError("invalid evidence envelope")
    if record["synthetic"] is not True:
        raise ValueError("synthetic-only evidence")
    commit = record["commit"]
    if not isinstance(commit, str) or SHA.fullmatch(commit) is None:
        raise ValueError("exact Git commit required")
    checks = record["checks"]
    if not isinstance(checks, Mapping) or set(checks) != set(CHECKS):
        raise ValueError("missing or unknown acceptance checks")
    outcomes = []
    for name in CHECKS:
        item = checks[name]
        if not isinstance(item, Mapping) or set(item) != {"status", "evidence_commit"}:
            raise ValueError("invalid check schema")
        status, evidence = item["status"], item["evidence_commit"]
        if not isinstance(status, str) or status not in STATUSES:
            raise ValueError("invalid check status")
        if status == "PASS":
            if not isinstance(evidence, str) or evidence != commit:
                raise ValueError("PASS requires exact-head evidence")
        elif evidence is not None:
            raise ValueError("non-PASS checks cannot claim evidence")
        outcomes.append(status)
    return {
        "synthetic": True,
        "commit": commit,
        "internal_rehearsal": "PENDING_INDEPENDENT_VERIFICATION" if all(s == "PASS" for s in outcomes) else "NO_GO",
        "evidence_verified": False,
        "production_pilot_authorized": False,
        "verified_customers": None,
        "verified_net_profit_cents": None,
        "failed_checks": tuple(name for name in CHECKS if checks[name]["status"] == "FAIL"),
        "not_run_checks": tuple(name for name in CHECKS if checks[name]["status"] == "NOT_RUN"),
    }
