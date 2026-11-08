"""Offline cash-basis subscription net calculator; synthetic scenarios only.

This cannot authenticate receipts, invoices, expenses, or customers.
No network, persistence, billing, contact, or production side effects.
"""
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

FIELDS = (
    "settled_collections", "refunds", "chargebacks", "processing_fees",
    "infrastructure", "provider_usage", "support_labor",
    "sales_marketing", "allocated_overhead", "other_operating_costs",
    "owner_labor_imputed",
)


@dataclass(frozen=True)
class SyntheticNetResult:
    synthetic: bool
    verified_profit: bool
    pretax_cash_operating_net_cents: int
    pretax_economic_net_cents: int
    target_met_verified: bool


def _cents(value: str) -> int:
    # Strings only: avoid binary float errors, scientific notation and NaN.
    if type(value) is not str or len(value) > 18:
        raise ValueError("Use bounded canonical decimal strings")
    import re
    if not re.fullmatch(r"(?:0|[1-9][0-9]{0,11})(?:\.[0-9]{1,2})?", value):
        raise ValueError("Use nonnegative decimal amounts with <=2 fractional digits")
    try:
        amount = Decimal(value) * 100
    except InvalidOperation as exc:
        raise ValueError("Invalid amount") from exc
    return int(amount)


def calculate_synthetic_net(amounts: dict) -> SyntheticNetResult:
    """Require every cost category explicitly; never infer verified revenue."""
    if type(amounts) is not dict or set(amounts) != set(FIELDS):
        raise ValueError("All and only approved financial fields are required")
    values = {name: _cents(amounts[name]) for name in FIELDS}
    costs = sum(values[name] for name in FIELDS if name not in
                ("settled_collections", "owner_labor_imputed"))
    cash = values["settled_collections"] - costs
    return SyntheticNetResult(
        synthetic=True, verified_profit=False,
        pretax_cash_operating_net_cents=cash,
        pretax_economic_net_cents=cash - values["owner_labor_imputed"],
        target_met_verified=False,
    )
