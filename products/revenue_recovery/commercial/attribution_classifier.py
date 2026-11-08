"""Offline, synthetic-only commercial attribution classifier.

No network, persistence, provider connections, payment processing or PII.
This module cannot verify real receipts. It deliberately never labels a
single associated sale as incrementally recovered revenue.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SyntheticReceipt:
    synthetic: bool
    settled: bool
    tenant_join_valid: bool
    duplicate: bool
    refund_reconciled: bool
    rre_linked: bool
    reviewed_before_action: bool
    confounding_touch: bool


def classify_receipt(receipt: SyntheticReceipt) -> str:
    """Classify one *synthetic* receipt, fail closed on invalid input.

    Return one of unverified, paid_unattributed, associated_confounded,
    associated_observed. No causal uplift is inferred from a single record.
    """
    if type(receipt) is not SyntheticReceipt:
        raise TypeError("SyntheticReceipt required")
    if any(type(getattr(receipt, name)) is not bool for name in receipt.__dataclass_fields__):
        raise ValueError("all receipt flags must be booleans")
    if (not receipt.synthetic or not receipt.settled
            or not receipt.tenant_join_valid or receipt.duplicate
            or not receipt.refund_reconciled):
        return "unverified"
    if not receipt.rre_linked:
        return "paid_unattributed"
    if receipt.confounding_touch or not receipt.reviewed_before_action:
        return "associated_confounded"
    return "associated_observed"
