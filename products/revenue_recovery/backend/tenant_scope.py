"""Pure synthetic tenant-scope exercise; NOT authentication or a production datastore.

This module is intentionally not exposed by backend.app or any public route.
The caller can construct DemoPrincipal, so its fields are NOT cryptographic
identity proof. Only a future vetted IdP adapter plus private, RLS-enforced DB
can establish real authentication and tenant authorization.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from threading import RLock
from typing import Any

from backend.app import DemoStore

_DEMO_TENANT = re.compile(r"DEMO-TENANT-[A-Za-z0-9_-]{1,32}\Z")
_DEMO_SUBJECT = re.compile(r"DEMO-ACTOR-[A-Za-z0-9_-]{1,32}\Z")
_ROLES = frozenset({"viewer", "reviewer", "operator"})
_PERMISSION_MAP = {
    "viewer": frozenset({"read"}),
    "reviewer": frozenset({"read", "prepare_review"}),
    "operator": frozenset({"read", "prepare_review", "simulate_intake"}),
}
_PROHIBITED_REAL_ACTIONS = frozenset({
    "send", "sms", "email", "call", "book", "charge", "refund",
    "verify_real_payment", "ingest_real_customer", "change_membership",
})


class TenantScopeDenied(PermissionError):
    """Inaccessible synthetic tenant or action."""


@dataclass(frozen=True)
class DemoPrincipal:
    """Fixture identity, not verified login, JWT, OIDC, or staff authorization."""
    tenant_id: str
    subject_id: str
    role: str
    synthetic: bool = True

    def __post_init__(self) -> None:
        if (self.synthetic is not True
                or not isinstance(self.tenant_id, str)
                or _DEMO_TENANT.fullmatch(self.tenant_id) is None
                or not isinstance(self.subject_id, str)
                or _DEMO_SUBJECT.fullmatch(self.subject_id) is None
                or not isinstance(self.role, str)
                or self.role not in _ROLES):
            raise TenantScopeDenied("Only explicitly synthetic fixture principals allowed")


def require_demo_permission(
    principal: DemoPrincipal,
    target_tenant: str,
    action: str,
) -> None:
    """Fail closed and do not leak target tenant existence.

    This helper is useful for synthetic tests only. A forged DemoPrincipal
    remains a forged fixture; do not use it to secure a real HTTP request.
    """
    if not isinstance(principal, DemoPrincipal):
        raise TenantScopeDenied("No verified fixture actor")
    if not isinstance(target_tenant, str) or target_tenant != principal.tenant_id:
        raise TenantScopeDenied("Tenant boundary violation")
    if not isinstance(action, str) or action in _PROHIBITED_REAL_ACTIONS:
        raise TenantScopeDenied("Real-world action disabled")
    if action not in _PERMISSION_MAP[principal.role]:
        raise TenantScopeDenied("Action not permitted in demo")


class TenantScopedDemoStore:
    """Isolated, process-memory-only synthetic queues; no real authentication.

    Each tenant gets a separate strict DemoStore. The interface NEVER accepts
    arbitrary recipient addresses or real identifiers and NEVER calls a
    networked CRM or provider. This is a regression fixture, not persistence.
    """
    def __init__(self) -> None:
        self._lock = RLock()
        self._spaces: dict[str, DemoStore] = {}

    def ingest(self, principal: DemoPrincipal, tenant_id: str, lead: object) -> tuple[dict, bool]:
        require_demo_permission(principal, tenant_id, "simulate_intake")
        with self._lock:
            space = self._spaces.setdefault(tenant_id, DemoStore())
        return space.add(lead)

    def read(self, principal: DemoPrincipal, tenant_id: str, reference: str) -> dict | None:
        require_demo_permission(principal, tenant_id, "read")
        if not isinstance(reference, str) or len(reference) > 64:
            raise TenantScopeDenied("Invalid synthetic reference")
        with self._lock:
            space = self._spaces.get(tenant_id)
        return space.get(reference) if space else None

    def list(self, principal: DemoPrincipal, tenant_id: str) -> list[dict]:
        require_demo_permission(principal, tenant_id, "read")
        with self._lock:
            space = self._spaces.get(tenant_id)
        return space.list() if space else []

    def prepare_review(self, principal: DemoPrincipal, tenant_id: str, reference: str) -> dict[str, Any]:
        require_demo_permission(principal, tenant_id, "prepare_review")
        lead = self.read(principal, tenant_id, reference)
        if lead is None:
            raise TenantScopeDenied("Unknown synthetic reference")
        return {
            "synthetic": True,
            "tenant_id": tenant_id,
            "external_ref": lead["external_ref"],
            "review_required": True,
            "identity_verified": False,
            "recipient_consent_verified": False,
            "transmitted": False,
            "actual_appointment_confirmed": False,
            "actual_payment_verified": False,
        }
