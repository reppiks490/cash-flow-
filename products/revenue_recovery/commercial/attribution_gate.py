"""Offline commercial evidence classification; never infer paid outcomes from demos."""
from __future__ import annotations

from decimal import Decimal
import re

_MONEY = re.compile(r"(?:0|[1-9][0-9]{0,8})(?:\.[0-9]{1,2})?\Z")


def classify_attribution(event: dict) -> dict:
    """Fail closed on non-receipt evidence; no external I/O or customer fields.

    Only enumerated synthetic event types are accepted. Even a mock 'closed'
    event never becomes verified revenue.
    """
    if type(event) is not dict or set(event) != {"event_type", "synthetic", "amount_usd", "evidence"}:
        raise ValueError("Unexpected event schema")
    if event["synthetic"] is not True:
        raise ValueError("Live financial evidence is not accepted")
    if event["event_type"] not in ("inquiry", "draft", "appointment_mock", "closed_job_mock"):
        raise ValueError("Unsupported event")
    if event["evidence"] != "offline_fixture":
        raise ValueError("Only offline fixtures are supported")
    amount = event["amount_usd"]
    if type(amount) is not str or not _MONEY.fullmatch(amount):
        raise ValueError("Invalid amount")
    value = Decimal(amount)
    if value > Decimal("100000000"):
        raise ValueError("Amount outside synthetic bounds")
    if event["event_type"] in ("inquiry", "draft", "appointment_mock") and value != 0:
        raise ValueError("Non-closed stages cannot carry amounts")
    return {
        "event_type": event["event_type"],
        "synthetic": True,
        "estimated_pipeline_usd": str(value.quantize(Decimal("0.01"))) if event["event_type"] == "closed_job_mock" else None,
        "verified_collected_revenue_usd": None,
        "verified_net_profit_usd": None,
        "receipt_verified": False,
        "customer_count_verified": None,
        "external_actions_enabled": False,
    }
