"""Model-agnostic, offline-only provider protocol.

No vendor SDK, network client, keys, environment-based provider selection or
external calls. Model-generated content is intentionally not claimed.
"""
from __future__ import annotations
from collections.abc import Mapping
from typing import Protocol
from .qualification import qualify_lead
from .followups import prepare_followup

class QualificationProvider(Protocol):
    def qualify(self, lead: Mapping[str, object], *, opted_out: bool | None = None) -> dict[str, object]: ...
    def draft(self, lead: Mapping[str, object], *, opted_out: bool | None = None, objection: str | None = None) -> dict[str, object]: ...

class OfflineRulesProvider:
    provider_id = "offline-deterministic-rules-v1"
    uses_model = False
    external_calls = False

    def qualify(self, lead: Mapping[str, object], *, opted_out: bool | None = None) -> dict[str, object]:
        return qualify_lead(lead, opted_out=opted_out)

    def draft(self, lead: Mapping[str, object], *, opted_out: bool | None = None,
              objection: str | None = None) -> dict[str, object]:
        return prepare_followup(lead, opted_out=opted_out, objection=objection)

def get_provider(name: str = "offline") -> QualificationProvider:
    if name != "offline":
        raise ValueError("Only the offline rules provider is enabled; no external models configured")
    return OfflineRulesProvider()

def preview_offline_bundle(lead: Mapping[str, object], *, opted_out: bool | None = None,
                           objection: str | None = None) -> dict[str, object]:
    """Compute an inert, coherent qualification/draft snapshot.

    No remote provider can be selected here. Neither mock consent nor human
    review turns this output into permission to contact a real person.
    """
    provider = get_provider("offline")
    if provider.uses_model is not False or provider.external_calls is not False:
        raise ValueError("Offline preview cannot execute model or network providers")
    qualification = provider.qualify(lead, opted_out=opted_out)
    followup = provider.draft(lead, opted_out=opted_out, objection=objection)
    if (qualification != followup.get("qualification")
            or qualification.get("outreach_allowed") is not False
            or followup.get("sent") is not False
            or followup.get("send_enabled") is not False
            or followup.get("requires_human_approval") is not True
            or followup.get("external_ref") != qualification.get("external_ref")
            or (opted_out is True and
                (followup.get("draft") is not None or followup.get("status") != "suppressed"))):
        raise ValueError("Unsafe or inconsistent offline preview")
    return {
        "schema_version": "rre-offline-bundle-v1",
        "synthetic": True,
        "provider_id": provider.provider_id,
        "uses_model": False,
        "external_calls": False,
        "outreach_allowed": False,
        "sent": False,
        "send_enabled": False,
        "requires_human_approval": True,
        "qualification": qualification,
        "followup": followup,
    }
