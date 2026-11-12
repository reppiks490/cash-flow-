"""Pure, synthetic-only HVAC buyer-value thresholds; never a ROI claim.

Uses no provider calls, user identifiers, contacts, stored data, or billing.
Job contribution and staff time are alternative thought experiments, not
additive cash flows or evidence of value delivered.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

_AMOUNT = re.compile(r"(?:0|[1-9][0-9]{0,6})(?:\.[0-9]{1,2})?\Z", re.ASCII)


class BuyerValueError(ValueError):
    """Unsafe or unsupported synthetic buyer-value assumption."""


@dataclass(frozen=True)
class BuyerValueInputs:
    monthly_price_usd: str
    incremental_job_contribution_usd: str
    loaded_labor_hour_cost_usd: str


def _cents(value: str, maximum: int) -> int:
    if type(value) is not str or not _AMOUNT.fullmatch(value):
        raise BuyerValueError("Expected bounded canonical plain USD decimal string")
    dollars, _, fraction = value.partition(".")
    cents = int(dollars) * 100 + int(fraction.ljust(2, "0") or "0")
    if cents > maximum:
        raise BuyerValueError("Synthetic USD assumption exceeds approved maximum")
    return cents


def _money(cents: int) -> str:
    return f"{cents // 100}.{cents % 100:02d}"


def calculate_buyer_break_even(inputs: BuyerValueInputs) -> dict:
    """Compute *separate* arithmetic thresholds, never verified ROI or cash.

    Job contribution means hypothetical incremental net contribution AFTER
    that job's costs, not quote face value. Staff-hours equivalent is a labor
    opportunity-cost comparison, NOT a claim that payroll costs decline.
    This function deliberately does not add either threshold into a ROI total.
    """
    if type(inputs) is not BuyerValueInputs:
        raise BuyerValueError("Expected synthetic buyer-value assumption record")
    price = _cents(inputs.monthly_price_usd, 1_000_000)  # $10,000/month cap
    contribution = _cents(inputs.incremental_job_contribution_usd, 100_000_000)
    labor_rate = _cents(inputs.loaded_labor_hour_cost_usd, 1_000_000)
    if price == 0:
        raise BuyerValueError("Hypothetical monthly subscription price must be positive")
    jobs = (price + contribution - 1) // contribution if contribution else None
    hundredth_hours = (price * 100 + labor_rate - 1) // labor_rate if labor_rate else None
    return {
        "classification": "unvalidated_buyer_value_hypothesis",
        "synthetic": True,
        "industry": "hvac",
        "monthly_price_usd": _money(price),
        "jobs_required_to_cover_subscription_scenario": jobs,
        "staff_hours_equivalent_to_subscription_scenario": (
            _money(hundredth_hours) if hundredth_hours is not None else None
        ),
        "job_contribution_is_not_revenue": True,
        "staff_hours_equivalent_is_not_cash_savings": True,
        "verified_incremental_jobs": None,
        "verified_staff_time_saved_hours": None,
        "verified_customer_recovered_revenue_usd": None,
        "verified_rre_net_profit_usd": None,
        "outreach_enabled": False,
        "billing_enabled": False,
    }
