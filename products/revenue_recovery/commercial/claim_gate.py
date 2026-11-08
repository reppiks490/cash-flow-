"""Offline, fail-closed classification of synthetic HVAC commercial claims.

This module never verifies payments, customers, causality, or operator authority.
It only prevents unsupported claims from being rendered as verified.
"""
from __future__ import annotations

from dataclasses import dataclass

_ALLOWED = frozenset({"synthetic_demo", "pricing_hypothesis", "verified_revenue", "verified_net_profit"})


@dataclass(frozen=True)
class ClaimDecision:
    label: str
    displayable: bool
    verified: bool
    reason: str
    live_action_authorized: bool = False


def classify_claim(kind: object, evidence: object = None) -> ClaimDecision:
    """Classify a proposed claim without accepting caller-supplied proof.

    Financial claims require authenticated private reconciliation, which this
    offline module cannot perform. Caller evidence is deliberately ignored.
    """
    if type(kind) is not str or kind not in _ALLOWED:
        raise ValueError("Unsupported commercial claim category")
    if evidence is not None:
        raise ValueError("Evidence cannot be authenticated by the offline classifier")
    if kind == "synthetic_demo":
        return ClaimDecision(kind, True, False, "Synthetic demonstration only")
    if kind == "pricing_hypothesis":
        return ClaimDecision(kind, True, False, "Unvalidated pricing assumption")
    return ClaimDecision(kind, False, False, "Requires authenticated private financial reconciliation")
