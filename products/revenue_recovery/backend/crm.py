"""Pure, non-network CRM interoperability adapter for synthetic demo records.

This is intentionally NOT a connected CRM integration. Production requires
authentication, tenant isolation, consent verification and vendor-specific APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import re

_REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z", re.ASCII)
# These enums mirror the synthetic demo intake contract; arbitrary free text can
# contain personal data and must not enter a public-repository demonstration.
_SOURCES = frozenset({"website", "phone", "referral"})
_NEEDS = frozenset({"AC not cooling", "estimate follow-up", "AC maintenance"})


@dataclass(frozen=True)
class CRMPreview:
    synthetic: bool
    external_ref: str
    source: str
    need: str
    proposed_stage: str
    dry_run: bool = True
    transmitted: bool = False


def preview_crm_record(lead: Mapping[str, object]) -> CRMPreview:
    """Return a safe mapping preview without network, disk or CRM side effects."""
    if lead.get("synthetic") is not True:
        raise ValueError("Only explicitly synthetic leads are supported")
    allowed = {"synthetic", "external_ref", "source", "need", "status"}
    if set(lead) - allowed:
        raise ValueError("Unexpected fields: do not submit PII to the demo adapter")
    for key in ("external_ref", "source", "need"):
        value = lead.get(key)
        if not isinstance(value, str) or not 1 <= len(value.strip()) <= 240:
            raise ValueError(f"{key} must be a nonempty string of at most 240 characters")
    if not _REFERENCE.fullmatch(str(lead["external_ref"])):
        raise ValueError("external_ref must be an ASCII synthetic token")
    if lead["source"] not in _SOURCES:
        raise ValueError("Unsupported synthetic source")
    if lead["need"] not in _NEEDS:
        raise ValueError("Unsupported synthetic need")
    if lead.get("status") not in (None, "received"):
        raise ValueError("Unsupported lead stage")
    return CRMPreview(
        synthetic=True,
        external_ref=str(lead["external_ref"]).strip(),
        source=str(lead["source"]).strip(),
        need=str(lead["need"]).strip(),
        proposed_stage="new_inquiry",
    )
