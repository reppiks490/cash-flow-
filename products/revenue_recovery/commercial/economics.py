"""Side-effect-free RRE subscription scenario calculator.

Planning arithmetic only: NO verified revenue, customer, receipt, charging,
payment processing, bank transfer, or customer activation is represented.
All amounts are USD cents; never process or record real customer data here.
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_CEILING
import re

MAX_CUSTOMERS = 100_000
MAX_DOLLARS = Decimal("10000000.00")


class ScenarioError(ValueError):
    """Invalid or unsupported planning assumption."""


def _cents(value: str, name: str, *, positive: bool = False) -> int:
    if type(value) is not str or not re.fullmatch(
        r"(?:0|[1-9][0-9]{0,7})(?:\.[0-9]{1,2})?\Z", value, flags=re.ASCII
    ):
        raise ScenarioError(f"{name} must be a bounded plain USD decimal string")
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError):
        raise ScenarioError(f"{name} must be valid USD") from None
    if not number.is_finite() or number < 0 or number > MAX_DOLLARS:
        raise ScenarioError(f"{name} must be a finite nonnegative USD amount")
    if positive and number == 0:
        raise ScenarioError(f"{name} must be positive")
    if number.as_tuple().exponent < -2:
        raise ScenarioError(f"{name} must not exceed two decimal places")
    return int(number * 100)


def model_subscription_scenario(
    *,
    customers: int,
    monthly_price_usd: str,
    fixed_monthly_cost_usd: str,
    variable_monthly_cost_per_customer_usd: str,
    target_profit_usd: str = "2500.00",
    processor_rate_bps: int = 0,
    processor_flat_fee_usd: str = "0.00",
) -> dict:
    """Return explicit hypothetical MRR, costs and target math.

    Assumes one charge per paying customer per month, no refunds or taxes,
    and that all support labor, owner labor, acquisition, compliance, hosting
    and other material expenses have been included in user-supplied costs.
    The function cannot validate those assumptions and therefore never
    returns a verified revenue or profit figure.
    """
    if type(customers) is not int or not 0 <= customers <= MAX_CUSTOMERS:
        raise ScenarioError("customers must be an integer between 0 and 100000")
    if type(processor_rate_bps) is not int or not 0 <= processor_rate_bps <= 10_000:
        raise ScenarioError("processor_rate_bps must be an integer from 0 to 10000")

    price = _cents(monthly_price_usd, "monthly_price_usd", positive=True)
    fixed = _cents(fixed_monthly_cost_usd, "fixed_monthly_cost_usd")
    variable = _cents(variable_monthly_cost_per_customer_usd, "variable_monthly_cost_per_customer_usd")
    target = _cents(target_profit_usd, "target_profit_usd")
    flat_fee = _cents(processor_flat_fee_usd, "processor_flat_fee_usd")

    # ROUND_CEILING conservatively budgets partial cents of a transaction fee.
    rate_fee = int((Decimal(price) * Decimal(processor_rate_bps) / Decimal(10_000))
                   .to_integral_value(rounding=ROUND_CEILING))
    fee_per_customer = rate_fee + flat_fee
    contribution = price - variable - fee_per_customer
    gross = customers * price
    fees = customers * fee_per_customer
    all_costs = fixed + customers * variable + fees
    profit = gross - all_costs

    needed = None
    if target + fixed == 0:
        needed = 0
    elif contribution > 0:
        shortfall = target + fixed
        needed = (shortfall + contribution - 1) // contribution

    return {
        "type": "hypothetical_subscription_scenario",
        "planning_only": True,
        "verified_customers": None,
        "verified_gross_revenue_cents": None,
        "verified_net_profit_cents": None,
        "customers_assumed": customers,
        "gross_mrr_cents": gross,
        "fixed_costs_cents": fixed,
        "variable_costs_cents": variable * customers,
        "processor_fees_cents": fees,
        "estimated_total_costs_cents": all_costs,
        "estimated_pre_tax_profit_cents": profit,
        "target_profit_cents": target,
        "scenario_meets_target": profit >= target,
        "minimum_customers_for_target": needed,
        "minimum_customers_outside_supported_range": needed is not None and needed > MAX_CUSTOMERS,
        "assumptions": [
            "One successful subscription charge per assumed paying customer monthly",
            "No refunds, chargebacks, sales tax or income tax modeled",
            "Owner labor, customer support, acquisition, hosting, integrations, legal and compliance costs must be included in supplied costs",
            "All customers, prices and costs are unverified planning inputs",
        ],
    }
