"""Offline, hypothetical HVAC subscription economics. No receipts or billing.

All inputs are scenario assumptions, never observations of customers or sales.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import re

_AMOUNT = re.compile(r"(?:0|[1-9][0-9]{0,7})(?:\.[0-9]{1,2})?\Z", re.ASCII)
_COUNT = re.compile(r"(?:0|[1-9][0-9]{0,5})\Z", re.ASCII)


def _money(value: str) -> Decimal:
    if type(value) is not str or not _AMOUNT.fullmatch(value):
        raise ValueError("Use bounded nonnegative USD decimal strings (two decimals max)")
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc


@dataclass(frozen=True)
class Scenario:
    monthly_price_usd: str = "700.00"
    customers: int = 5
    monthly_fixed_cost_usd: str = "500.00"
    monthly_cost_per_customer_usd: str = "75.00"
    monthly_target_net_usd: str = "2500.00"


def evaluate(scenario: Scenario) -> dict:
    """Return an assumption-only monthly operating contribution scenario.

    Excludes taxes, owner compensation, refunds, payment fees, acquisition costs
    and other expenses unless the operator explicitly includes them in costs.
    """
    if type(scenario) is not Scenario:
        raise ValueError("Scenario required")
    if type(scenario.customers) is not int or not 0 <= scenario.customers <= 100000:
        raise ValueError("Invalid hypothetical customer count")
    price = _money(scenario.monthly_price_usd)
    fixed = _money(scenario.monthly_fixed_cost_usd)
    variable = _money(scenario.monthly_cost_per_customer_usd)
    target = _money(scenario.monthly_target_net_usd)
    gross = price * scenario.customers
    costs = fixed + variable * scenario.customers
    contribution = gross - costs
    unit_margin = price - variable
    if unit_margin <= 0:
        needed = None
    else:
        needed = int(((target + fixed) / unit_margin).to_integral_value(rounding=ROUND_CEILING))
        if needed > 100000:
            needed = None
    return {
        "classification": "hypothetical_not_verified",
        "verified_revenue_usd": "0.00",
        "verified_net_profit_usd": "0.00",
        "hypothetical_customers": scenario.customers,
        "hypothetical_gross_usd": f"{gross:.2f}",
        "hypothetical_costs_usd": f"{costs:.2f}",
        "hypothetical_contribution_usd": f"{contribution:.2f}",
        "target_net_usd": f"{target:.2f}",
        "minimum_customers_for_target_under_assumptions": needed,
        "target_is_verified": False,
        "billing_enabled": False,
        "excluded_costs": ["taxes", "owner_compensation", "refunds", "payment_fees", "customer_acquisition", "other_unmodeled_costs"],
    }
