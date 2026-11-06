"""Offline, synthetic-only commercial KPI accounting. No payments or CRM writes."""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal

class MeasurementError(ValueError):
    """Unsafe, inconsistent or unsupported financial evidence."""

# Before Decimal parsing, reject noncanonical or unbounded monetary inputs.
# Exponents such as 1E+999999 must never escape as decimal.InvalidOperation.
_USD_RE = re.compile(r"(?:0|[1-9][0-9]{0,7})(?:\.[0-9]{1,2})?\Z", re.ASCII)
_MAX_SCENARIO_USD = Decimal("10000000.00")

def usd(value: str) -> Decimal:
    """Bounded plain USD scenario amount; never an authenticated receipt."""
    if type(value) is not str or not _USD_RE.fullmatch(value):
        raise MeasurementError("Amount must be a bounded nonnegative plain USD decimal string")
    amount = Decimal(value)
    if amount > _MAX_SCENARIO_USD:
        raise MeasurementError("Amount exceeds the synthetic planning limit")
    return amount.quantize(Decimal("0.01"))

@dataclass(frozen=True)
class SyntheticMonthlySnapshot:
    """Scenario arithmetic only: never represent these values as verified receipts."""
    subscriptions: int
    price_usd: str
    refunds_usd: str
    direct_costs_usd: str
    overhead_usd: str
    synthetic: bool = True

    def evaluate(self) -> dict:
        if self.synthetic is not True:
            raise MeasurementError("Real-world accounting is not supported")
        if type(self.subscriptions) is not int or self.subscriptions < 0:
            raise MeasurementError("Subscription count must be a nonnegative integer")
        if self.subscriptions > 1000000:
            raise MeasurementError("Scenario subscription count out of range")
        gross = usd(self.price_usd) * self.subscriptions
        refunds = usd(self.refunds_usd)
        direct = usd(self.direct_costs_usd)
        overhead = usd(self.overhead_usd)
        if refunds > gross:
            raise MeasurementError("Refunds cannot exceed modeled gross")
        net = gross - refunds - direct - overhead
        return {
            "synthetic": True,
            "verified": False,
            "gross_billed_scenario_usd": str(gross),
            "net_profit_scenario_usd": str(net),
            "target_met_in_scenario": net >= Decimal("2500.00"),
            "verified_receipts_usd": None,
            "verified_net_profit_usd": None,
            "customer_recovered_revenue_usd": None,
        }
