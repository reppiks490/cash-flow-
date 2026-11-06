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
    def draft(self, lead: Mapping[str, object], *, opted_out: bool | None = None) -> dict[str, object]: ...

class OfflineRulesProvider:
    provider_id = "offline-deterministic-rules-v1"
    uses_model = False
    external_calls = False

    def qualify(self, lead: Mapping[str, object], *, opted_out: bool | None = None) -> dict[str, object]:
        return qualify_lead(lead, opted_out=opted_out)

    def draft(self, lead: Mapping[str, object], *, opted_out: bool | None = None) -> dict[str, object]:
        return prepare_followup(lead, opted_out=opted_out)

def get_provider(name: str = "offline") -> QualificationProvider:
    if name != "offline":
        raise ValueError("Only the offline rules provider is enabled; no external models configured")
    return OfflineRulesProvider()
