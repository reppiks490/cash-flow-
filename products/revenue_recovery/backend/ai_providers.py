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

_TRUSTED_QUALIFY = OfflineRulesProvider.__dict__["qualify"]
_TRUSTED_DRAFT = OfflineRulesProvider.__dict__["draft"]

def get_provider(name: str = "offline") -> QualificationProvider:
    if name != "offline":
        raise ValueError("Only the offline rules provider is enabled; no external models configured")
    return OfflineRulesProvider()


def build_offline_review_envelope(
    lead: Mapping[str, object], *,
    opted_out: bool | None = None,
    objection: str | None = None,
    provider_name: str = "offline",
) -> dict[str, object]:
    """Return a synthetic-only, no-send, versioned review snapshot.

    The caller-supplied `opted_out` flag is only a mock fixture. This pure
    adapter does not check lawful consent, authenticate an operator, persist
    decisions, authorize outreach, or perform model inference or I/O.
    Unknown providers are rejected *before* invoking any provider methods.
    """
    # Reject class-level monkeypatching before constructing or invoking the adapter.
    # This is a defense-in-depth integrity check, not a hostile-runtime sandbox.
    if (OfflineRulesProvider.__dict__.get("qualify") is not _TRUSTED_QUALIFY
            or OfflineRulesProvider.__dict__.get("draft") is not _TRUSTED_DRAFT):
        raise ValueError("Untrusted offline provider class methods")
    provider = get_provider(provider_name)
    # The only enabled adapter is the built-in deterministic implementation.
    # A replacement object can reproduce safe outputs while forging provenance.
    # Reject subclasses/proxies as well: their behavior and identity are untrusted.
    if type(provider) is not OfflineRulesProvider or provider.provider_id != OfflineRulesProvider.provider_id:
        raise ValueError("Untrusted offline provider identity")
    if (OfflineRulesProvider.__dict__.get("provider_id") != "offline-deterministic-rules-v1"
            or OfflineRulesProvider.__dict__.get("uses_model") is not False
            or OfflineRulesProvider.__dict__.get("external_calls") is not False):
        raise ValueError("Untrusted offline provider class metadata")
    if provider.uses_model is not False or provider.external_calls is not False:
        raise ValueError("Only a proven offline deterministic provider is permitted")
    # Freeze the expected deterministic result before any provider method runs.
    # A falsely labelled offline adapter must not introduce forged confidence,
    # a different reference, unsupported text, or a send-enabled response.
    expected_qualification = qualify_lead(lead, opted_out=opted_out)
    expected_followup = prepare_followup(
        lead, opted_out=opted_out, objection=objection
    )
    qualification = provider.qualify(dict(lead), opted_out=opted_out)
    followup = provider.draft(dict(lead), opted_out=opted_out, objection=objection)
    suppressed = opted_out is True
    if (
        not isinstance(qualification, Mapping)
        or not isinstance(followup, Mapping)
        or dict(qualification) != expected_qualification
        or dict(followup) != expected_followup
        or qualification.get("synthetic") is not True
        or followup.get("synthetic") is not True
        or qualification.get("external_ref") != followup.get("external_ref")
        or followup.get("qualification") != qualification
        or qualification.get("outreach_allowed") is not False
        or followup.get("sent") is not False
        or followup.get("send_enabled") is not False
        or followup.get("requires_human_approval") is not True
        or followup.get("status") != (
            "suppressed" if suppressed else "pending_human_review"
        )
        or (suppressed and followup.get("draft") is not None)
    ):
        raise ValueError("Unsafe offline review result")
    return {
        "schema_version": "rre-offline-review-v1",
        "synthetic": True,
        "provider_id": provider.provider_id,
        "generation_kind": "deterministic_rules_not_ai_inference",
        "uses_model": False,
        "external_calls": False,
        "outreach_enabled": False,
        "requires_human_approval": True,
        "qualification": qualification,
        "followup": followup,
    }

def preview_offline_bundle(lead: Mapping[str, object], *, opted_out: bool | None = None,
                           objection: str | None = None) -> dict[str, object]:
    """Compute an inert, coherent qualification/draft snapshot.

    No remote provider can be selected here. Neither mock consent nor human
    review turns this output into permission to contact a real person.
    """
    # Delegate to the single strict output and provider-identity validator.
    # No substituted provider methods execute before provenance checks.
    envelope = build_offline_review_envelope(
        lead, opted_out=opted_out, objection=objection, provider_name="offline"
    )
    return {
        "schema_version": "rre-offline-bundle-v1",
        "synthetic": True,
        "provider_id": envelope["provider_id"],
        "uses_model": False,
        "external_calls": False,
        "outreach_allowed": False,
        "sent": False,
        "send_enabled": False,
        "requires_human_approval": True,
        "qualification": envelope["qualification"],
        "followup": envelope["followup"],
    }
