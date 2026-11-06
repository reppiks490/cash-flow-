"""Pure, non-network CRM interoperability adapter for synthetic demo records.

This is intentionally NOT a connected CRM integration. Production requires
authentication, tenant isolation, consent verification and vendor-specific APIs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
from backend.qualification import validate_lead


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
    if not isinstance(lead, Mapping):
        raise ValueError("Lead must be a mapping")
    allowed = {"synthetic", "external_ref", "source", "need", "status"}
    if set(lead) - allowed:
        raise ValueError("Unexpected fields: customer information is not permitted")
    # An adapter may receive a valid intake payload without the stored status.
    # Normalize only that missing field; never silently accept 'paid' or 'booked'.
    complete = dict(lead)
    complete.setdefault("status", "received")
    row = validate_lead(complete)
    return CRMPreview(
        synthetic=True,
        external_ref=str(row["external_ref"]),
        source=str(row["source"]),
        need=str(row["need"]),
        proposed_stage="new_inquiry",
    )


def preview_crm_envelope(lead: Mapping[str, object]) -> dict[str, object]:
    """Vendor-neutral, JSON-compatible *preview*, never a provider write command.

    Only enum-validated synthetic fields cross this boundary. The fixed envelope
    deliberately contains no recipient, contact, credential, tenant or endpoint.
    A future live adapter must implement a separate authenticated interface.
    """
    record = preview_crm_record(lead)
    return {
        "schema_version": "rre.crm.preview.v1",
        "synthetic": True,
        "dry_run": True,
        "transmitted": False,
        "external_ref": record.external_ref,
        "source": record.source,
        "need": record.need,
        "proposed_stage": record.proposed_stage,
        "provider": None,
        "provider_record_id": None,
        "appointment_confirmed": False,
        "verified_recovered_revenue_cents": 0,
    }
