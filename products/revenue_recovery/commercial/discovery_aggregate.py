"""Synthetic-only, closed-schema HVAC discovery aggregation (no I/O)."""
from collections import Counter

FIELDS = {
    "record_class": {"synthetic"},
    "buyer_segment": {"solo", "2_10_staff", "11_plus_staff", "unknown"},
    "crm_family": {"jobber", "housecall_pro", "servicetitan", "hatch", "other", "none", "unknown"},
    "existing_automation": {"enabled", "disabled", "unknown"},
    "unresolved_gap": {"none", "missed_inquiry", "quote_followup", "cross_tool", "unknown"},
    "evidence_quality": {"self_report", "redacted_process_demo", "verified_private_audit", "unknown"},
    "preferred_offer": {"existing_crm_configuration", "one_time_audit", "managed_service", "software_only", "none", "unknown"},
    "700_usd_willingness": {"reject", "consider", "written_nonbinding", "unknown"},
    "blocking_reason": {"no_gap", "price", "security", "consent", "integration", "staffing", "unknown"},
    "authorization_state": {"not_authorized"},
    "outcome": {"hypothesis_only"},
}

def validate_synthetic_record(record):
    """Reject identifiers, extra keys, unknown enums and real research claims."""
    if type(record) is not dict or set(record) != set(FIELDS):
        raise ValueError("record must contain only the exact synthetic schema")
    for field, permitted in FIELDS.items():
        if type(record[field]) is not str or record[field] not in permitted:
            raise ValueError("invalid synthetic discovery field: " + field)
    return True

def summarize_synthetic(records):
    """Return only aggregate, explicitly non-evidentiary demo counts."""
    if type(records) not in (list, tuple) or len(records) > 1000:
        raise ValueError("bounded list or tuple required")
    for record in records:
        validate_synthetic_record(record)
    gaps = Counter(record["unresolved_gap"] for record in records)
    willingness = Counter(record["700_usd_willingness"] for record in records)
    return {
        "synthetic": True,
        "research_validated": False,
        "verified_customers": 0,
        "verified_collections_usd": 0,
        "verified_net_profit_usd": 0,
        "sample_size": len(records),
        "gap_counts": {key: gaps[key] for key in sorted(FIELDS["unresolved_gap"])},
        "willingness_counts": {key: willingness[key] for key in sorted(FIELDS["700_usd_willingness"])},
    }
