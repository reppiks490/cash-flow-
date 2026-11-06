"""Pure, hypothetical HVAC subscription unit-economics calculator.

No customer, payment, vendor or operational data is read or written.
All outputs are scenarios, never verified revenue or profit.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from decimal import Decimal, InvalidOperation, ROUND_CEILING

CENT = Decimal("0.01")
MAX_AMOUNT = Decimal("1000000.00")


class ScenarioError(ValueError):
    """Invalid or unsafe hypothetical inputs."""


def usd(value: str) -> Decimal:
    """Parse a finite nonnegative USD amount, strictly from a decimal string."""
    if type(value) is not str or not re.fullmatch(r"(?:0|[1-9][0-9]{0,6})(?:\\.[0-9]{1,2})?\\Z", value, flags=re.ASCII):
        raise ScenarioError("Amounts must be decimal strings")
    try:
        amount = Decimal(value)
    except InvalidOperation:
        raise ScenarioError("Invalid USD amount") from None
    if not amount.is_finite() or amount < 0 or amount > MAX_AMOUNT:
        raise ScenarioError("USD amount outside allowed range")
    if amount.as_tuple().exponent < -2:
        raise ScenarioError("Amounts must have at most two decimal places")
    return amount.quantize(CENT)


@dataclass(frozen=True)
class Scenario:
    customers: int
    price_usd: str
    variable_cost_per_customer_usd: str
    fixed_cost_usd: str
    acquisition_cost_usd: str
    refunds_and_fees_usd: str
    target_pretax_net_usd: str = "2500.00"


def calculate_scenario(s: Scenario) -> dict:
    """Return labeled arithmetic only; no actual financial verification."""
    if not isinstance(s, Scenario) or type(s.customers) is not int or not 0 <= s.customers <= 10000:
        raise ScenarioError("customers must be an integer between 0 and 10000")
    price = usd(s.price_usd)
    variable = usd(s.variable_cost_per_customer_usd)
    fixed = usd(s.fixed_cost_usd)
    acquisition = usd(s.acquisition_cost_usd)
    refunds = usd(s.refunds_and_fees_usd)
    target = usd(s.target_pretax_net_usd)
    gross = price * s.customers
    costs = variable * s.customers + fixed + acquisition + refunds
    net = gross - costs
    contribution = price - variable
    overhead = fixed + acquisition + refunds
    required = None
    if contribution > 0:
        required = max(0, int(((target + overhead) / contribution).to_integral_value(rounding=ROUND_CEILING)))
    return {
        "classification": "hypothetical_scenario_only",
        "synthetic": True,
        "verified_receipts": None,
        "actual_net_profit_usd": None,
        "customers_assumed": s.customers,
        "gross_billed_scenario_usd": str(gross.quantize(CENT)),
        "total_cost_scenario_usd": str(costs.quantize(CENT)),
        "pretax_net_scenario_usd": str(net.quantize(CENT)),
        "target_pretax_net_usd": str(target),
        "minimum_customers_for_target_scenario": required,
        "break_even_unreachable_at_assumed_unit_margin": required is None,
        "after_tax_net": None,
    }
