"""Additional synthetic-only buyer scenario; preserves buyer_break_even legacy API.

No external side effects, revenue verification, or payment operations.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
from .scenario_calculator import usd, ScenarioError

MAX_JOBS = 10000

@dataclass(frozen=True)
class BuyerScenario:
    subscription_usd: str
    incremental_paid_job_contribution_usd: str
    staff_hours_opportunity_cost_usd: str
    incremental_paid_jobs: int

def calculate_buyer_scenario(s: BuyerScenario) -> dict:
    """Illustrative additional staff opportunity cost, not realized ROI."""
    if type(s) is not BuyerScenario:
        raise ScenarioError("Expected BuyerScenario")
    if type(s.incremental_paid_jobs) is not int or not 0 <= s.incremental_paid_jobs <= MAX_JOBS:
        raise ScenarioError("Invalid incremental paid-job count")
    subscription = usd(s.subscription_usd)
    contribution = usd(s.incremental_paid_job_contribution_usd)
    staff = usd(s.staff_hours_opportunity_cost_usd)
    monthly_cost = subscription + staff
    threshold = (int((monthly_cost / contribution).to_integral_value(rounding=ROUND_CEILING))
                 if contribution > 0 else None)
    net = contribution * s.incremental_paid_jobs - monthly_cost
    return {
        "classification": "hypothetical_buyer_scenario_only",
        "synthetic": True,
        "verified_paid_jobs": None,
        "verified_buyer_roi": None,
        "actual_net_profit_usd": None,
        "seller_net_profit_usd": None,
        "assumed_incremental_paid_jobs": s.incremental_paid_jobs,
        "assumed_monthly_buyer_cost_usd": str(monthly_cost.quantize(Decimal("0.01"))),
        "hypothetical_buyer_net_value_usd": str(net.quantize(Decimal("0.01"))),
        "minimum_incremental_paid_jobs_to_break_even": threshold,
        "threshold_outside_supported_range": threshold is not None and threshold > MAX_JOBS,
        "break_even_unknown_due_to_zero_contribution": threshold is None,
    }
