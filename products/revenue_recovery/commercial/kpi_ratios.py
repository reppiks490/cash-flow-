"""Offline evidence-aware KPI ratios for synthetic HVAC pilot planning.

Pure functions only. No external communications, persistence, or revenue claims.
"""
from __future__ import annotations

from decimal import Decimal


def conversion_rate(numerator: int | None, denominator: int | None) -> dict[str, str | None]:
    """Return a percentage or unknown, never treating missing evidence as zero.

    Counts must be exact nonnegative integers (bool is not a count). A zero
    denominator has an undefined rate, not 0%. A numerator exceeding the
    denominator is inconsistent evidence and is rejected.
    """
    for name, value in (("numerator", numerator), ("denominator", denominator)):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"{name} must be a nonnegative integer or None")
    if numerator is None or denominator is None:
        return {"status": "unknown_missing_evidence", "percent": None}
    if numerator > denominator:
        raise ValueError("numerator cannot exceed denominator")
    if denominator == 0:
        return {"status": "undefined_zero_denominator", "percent": None}
    percent = (Decimal(numerator) * Decimal(100) / Decimal(denominator)).quantize(Decimal("0.01"))
    return {"status": "calculated_from_supplied_counts_not_verified", "percent": format(percent, ".2f")}
