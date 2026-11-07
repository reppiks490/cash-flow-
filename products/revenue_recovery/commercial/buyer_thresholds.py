"""Bounded, synthetic HVAC buyer-side subscription break-even arithmetic.

Separate from vendor-side scenario_calculator. No customer records or integrations.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
from .scenario_calculator import usd, ScenarioError, CENT

MAX_JOBS = 10000
MAX_HOURS = 10000


@dataclass(frozen=True)
class BuyerThreshold:
    monthly_subscription_usd: str
    contribution_per_incremental_paid_job_usd: str
    staff_hour_value_usd: str
    staff_hours_saved_per_month: int


def calculate_buyer_threshold(s: BuyerThreshold) -> dict:
    """Independent alternative break-even paths; never add both as realized ROI."""
    if not isinstance(s, BuyerThreshold):
        raise ScenarioError("Expected BuyerThreshold")
    if type(s.staff_hours_saved_per_month) is not int or not 0 <= s.staff_hours_saved_per_month <= MAX_HOURS:
        raise ScenarioError("staff_hours_saved_per_month must be a bounded integer")
    fee = usd(s.monthly_subscription_usd)
    job_contribution = usd(s.contribution_per_incremental_paid_job_usd)
    hourly_value = usd(s.staff_hour_value_usd)
    labor_value = (hourly_value * s.staff_hours_saved_per_month).quantize(CENT)
    jobs = None if job_contribution == 0 else int((fee / job_contribution).to_integral_value(rounding=ROUND_CEILING))
    hours = None if hourly_value == 0 else int((fee / hourly_value).to_integral_value(rounding=ROUND_CEILING))
    return {
        "classification": "hypothetical_buyer_threshold_only",
        "synthetic": True,
        "verified_incremental_paid_jobs": None,
        "verified_labor_savings": None,
        "actual_buyer_roi_usd": None,
        "monthly_subscription_scenario_usd": str(fee),
        "staff_labor_value_scenario_usd": str(labor_value),
        "minimum_incremental_paid_jobs_to_cover_fee": jobs if jobs is not None and jobs <= MAX_JOBS else None,
        "jobs_threshold_unknown": jobs is None,
        "jobs_threshold_outside_supported_range": jobs is not None and jobs > MAX_JOBS,
        "minimum_staff_hours_to_cover_fee": hours if hours is not None and hours <= MAX_HOURS else None,
        "hours_threshold_unknown": hours is None,
        "hours_threshold_outside_supported_range": hours is not None and hours > MAX_HOURS,
        "paths_are_alternatives_not_additive": True,
        "assumed_staff_hours_saved_per_month": s.staff_hours_saved_per_month,
    }
