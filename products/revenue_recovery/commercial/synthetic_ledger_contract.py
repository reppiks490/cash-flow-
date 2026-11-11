"""Synthetic-only, side-effect-free dual-ledger financial reconciliation.

Never accepts production receipts. This is a contract fixture, not accounting,
payment verification, or an operational integration.
"""
from decimal import Decimal, InvalidOperation
from collections import defaultdict
import re

_CANONICAL_USD = re.compile(r'(?:0|[1-9][0-9]{0,7})(?:\.[0-9]{1,2})?\Z', re.ASCII)

def _money(value):
    if type(value) is not str or not _CANONICAL_USD.fullmatch(value):
        raise ValueError("amount must be bounded canonical USD decimal string")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("invalid amount") from exc
    if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
        raise ValueError("amount must be finite, nonnegative cents")
    return amount

def reconcile(events, *, expenses_complete=False, expenses=()):
    """Return separate synthetic contractor and SaaS totals, never verified profit.

    Events: dicts with unique id, ledger (contractor|saas), kind
    (receipt|refund|chargeback), amount, synthetic=True, and parent_id
    for adjustments. Contractor receipts require attribution='confirmed'
    to count as attributable; ambiguous receipts remain un-attributed.
    """
    if type(expenses_complete) is not bool:
        raise ValueError("expenses_complete must be boolean")
    seen = {}
    totals = defaultdict(lambda: Decimal("0.00"))
    receipts = {}
    adjustments = defaultdict(lambda: Decimal("0.00"))
    if type(events) not in (list, tuple):
        raise ValueError("events must be a finite sequence")
    if type(expenses) not in (list, tuple):
        raise ValueError("expenses must be a finite sequence")
    if len(events) > 10000 or len(expenses) > 10000:
        raise ValueError("synthetic ledger input exceeds bounded batch size")
    for event in events:
        if not isinstance(event, dict) or event.get("synthetic") is not True:
            raise ValueError("synthetic events only")
        ident, ledger, kind = event.get("id"), event.get("ledger"), event.get("kind")
        if type(ident) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", ident, re.ASCII) or ident in seen:
            raise ValueError("missing or duplicate event id")
        if ledger not in ("contractor", "saas") or kind not in ("receipt", "refund", "chargeback"):
            raise ValueError("invalid ledger or kind")
        amount = _money(event.get("amount"))
        seen[ident] = True
        if kind == "receipt":
            if event.get("parent_id") is not None:
                raise ValueError("receipt cannot reference parent")
            attribution = event.get("attribution")
            if ledger == "contractor" and attribution not in ("confirmed", "ambiguous", "unknown"):
                raise ValueError("contractor attribution required")
            if ledger == "saas" and attribution is not None:
                raise ValueError("SaaS receipt cannot claim contractor attribution")
            receipts[ident] = (ledger, amount, attribution)
            totals[ledger + "_collected"] += amount
            if ledger == "contractor" and attribution == "confirmed":
                totals["contractor_attributable"] += amount
        else:
            parent = event.get("parent_id")
            if type(parent) is not str or parent not in receipts:
                raise ValueError("adjustment must reference preceding receipt")
            parent_ledger, original, attribution = receipts[parent]
            if ledger != parent_ledger:
                raise ValueError("cross-ledger adjustment prohibited")
            adjustments[parent] += amount
            if adjustments[parent] > original:
                raise ValueError("adjustments exceed receipt")
            totals[ledger + "_collected"] -= amount
            if ledger == "contractor" and attribution == "confirmed":
                totals["contractor_attributable"] -= amount
    costs = sum((_money(v) for v in expenses), Decimal("0.00"))
    return {
        "classification": "synthetic_contract_only",
        "contractor_collected_usd": str(totals["contractor_collected"].quantize(Decimal(".01"))),
        "contractor_attributable_usd": str(totals["contractor_attributable"].quantize(Decimal(".01"))),
        "saas_collected_usd": str(totals["saas_collected"].quantize(Decimal(".01"))),
        "synthetic_saas_contribution_usd": str((totals["saas_collected"] - costs).quantize(Decimal(".01"))) if expenses_complete else None,
        "verified_revenue_usd": None,
        "verified_net_profit_usd": None,
        "target_is_verified": False,
        "billing_enabled": False,
    }
