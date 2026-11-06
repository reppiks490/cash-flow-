"""Local-only, synthetic-lead HTTP prototype for Revenue Recovery Engine.

No customer information, outbound messaging, paid API calls or persistence are
supported. This process is deliberately unsuitable for public deployment.
"""

from __future__ import annotations

import argparse
import json
import re
import threading
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from backend.crm import preview_crm_record
from backend.ai_providers import get_provider
from backend.demo_evidence import SCENARIOS, aggregate_synthetic_scorecard, simulate_evidence_path

MAX_BODY_BYTES = 16_384
MAX_LEADS = 2_000
ALLOWED_SOURCES = frozenset({"demo", "website", "phone", "referral"})
ALLOWED_NEEDS = frozenset({"AC not cooling", "AC maintenance", "repair", "maintenance", "estimate follow-up", "heating issue"})
DEMO_REF = re.compile(r"(?:DEMO|QA)[-_][A-Za-z0-9_-]{1,56}\Z", re.I)


class LeadConflictError(ValueError):
    """An existing synthetic reference must not silently change identity."""


class DemoStore:
    """Process-local synthetic lead queue with idempotent external references."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._leads: dict[str, dict] = {}

    def add(self, incoming: object) -> tuple[dict, bool]:
        if not isinstance(incoming, dict):
            raise ValueError("Expected a JSON object")
        if incoming.get("synthetic") is not True:
            raise ValueError("Only explicitly synthetic demo leads are accepted")
        allowed = {"synthetic", "external_ref", "source", "need"}
        if set(incoming) - allowed:
            raise ValueError("Unexpected fields: PII and live customer data are not accepted")
        for key in ("external_ref", "source", "need"):
            value = incoming.get(key)
            if not isinstance(value, str) or not 1 <= len(value.strip()) <= 240:
                raise ValueError(f"{key} must be a nonempty string of at most 240 characters")
        external_ref = incoming["external_ref"].strip()
        if DEMO_REF.fullmatch(external_ref) is None:
            raise ValueError("external_ref must start with DEMO- or QA- and contain only a synthetic token")
        if incoming["source"] not in ALLOWED_SOURCES:
            raise ValueError("source must be a supported synthetic category")
        if incoming["need"] not in ALLOWED_NEEDS:
            raise ValueError("need must be a supported synthetic category")
        row = {
            "synthetic": True,
            "external_ref": external_ref,
            "source": incoming["source"].strip(),
            "need": incoming["need"].strip(),
            "status": "received",
        }
        with self._lock:
            if external_ref in self._leads:
                original = self._leads[external_ref]
                if original["source"] != row["source"] or original["need"] != row["need"]:
                    raise LeadConflictError("Duplicate synthetic reference has conflicting fields")
                return dict(original), False
            if len(self._leads) >= MAX_LEADS:
                raise ValueError("Demo capacity reached")
            self._leads[external_ref] = row
            return dict(row), True

    def list(self) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self._leads.values()]

    def get(self, external_ref: str) -> dict | None:
        with self._lock:
            row = self._leads.get(external_ref)
            return dict(row) if row is not None else None


def build_recovery_preview(lead: dict) -> dict:
    """Contract adapter from AI-lane offline rules to safe synthetic UI preview.

    Uses no LLM or external calls. No recipient identity, verified consent,
    outbound permission, booked appointment or financial receipt is available.
    All AI-lane outputs are verified to remain internal and unsent.
    """
    if lead.get("synthetic") is not True or lead.get("status") != "received":
        raise ValueError("Recovery preview requires a synthetic received lead")
    provider = get_provider("offline")
    assessment = provider.qualify(lead, opted_out=None)
    pending = provider.draft(lead, opted_out=None)
    if (
        provider.uses_model is not False or provider.external_calls is not False
        or assessment.get("schema_version") != "rre-qualification-v1"
        or assessment.get("decision") != "qualified_for_human_review"
        or assessment.get("outreach_allowed") is not False
        or pending.get("schema_version") != "rre-draft-v1"
        or pending.get("status") != "pending_human_review"
        or pending.get("sent") is not False
        or pending.get("send_enabled") is not False
        or pending.get("requires_human_approval") is not True
        or not isinstance(pending.get("draft"), str)
    ):
        raise ValueError("Offline qualification or draft failed closed")
    mapped = preview_crm_record(lead)
    return {
        "synthetic": True,
        "external_ref": lead["external_ref"],
        "qualification": {
            "result": "manual_review_required",
            "qualified": False,
            "decision_engine": provider.provider_id,
            "model_used": provider.uses_model,
            "consent_verified": False,
            "priority_score": assessment["priority_score"],
            "category": assessment["category"],
            "rubric": assessment,
        },
        "followup": {
            "status": "unsent_unapproved_draft",
            "approved": False,
            "transmitted": False,
            "message": "SYNTHETIC UNSENT DRAFT — deterministic rules, not an LLM:\n\n" +
                       pending["draft"],
            "template_status": pending["status"],
            "idempotency_key": pending["idempotency_key"],
        },
        "crm": asdict(mapped),
        "appointment": {
            "status": "not_requested",
            "confirmed": False,
            "transmitted": False,
            "booking_reference": None,
        },
        "attribution": {
            "verified_recovered_revenue_cents": 0,
            "verified_payment_receipts": 0,
            "revenue_source_connected": False,
            "business_subscription_revenue_verified": False,
        },
    }


def make_handler(store: DemoStore):
    """Local synthetic read-only previews and exact-allowlist UI assets."""
    web_dir = Path(__file__).resolve().parent.parent / "web"
    assets = {
        "/demo/": ("index.html", "text/html; charset=utf-8"),
        "/demo/app.js": ("app.js", "application/javascript; charset=utf-8"),
        "/demo/styles.css": ("styles.css", "text/css; charset=utf-8"),
    }

    class Handler(BaseHTTPRequestHandler):
        server_version = "RRE-Demo/0.2"

        def _valid_host(self) -> bool:
            host = self.headers.get("Host", "")
            return re.fullmatch(r"(?:localhost|127\.0\.0\.1)(?::[0-9]{1,5})?", host, re.I) is not None

        def _write(self, code: int, raw: bytes, mime: str) -> None:
            self.send_response(code)
            self.send_header("Content-Type", mime)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'none'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; img-src 'self' data:; base-uri 'none'; "
                "form-action 'none'; frame-ancestors 'none'",
            )
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _json(self, code: int, data: dict) -> None:
            self._write(code, json.dumps(data, sort_keys=True).encode("utf-8"),
                        "application/json; charset=utf-8")

        def do_GET(self) -> None:  # noqa: N802
            if not self._valid_host():
                self._json(403, {"error": "Loopback host required"})
                return
            if self.path == "/health":
                self._json(200, {"service": "revenue-recovery-demo", "status": "ok",
                                 "synthetic_only": True})
            elif self.path == "/api/demo/leads":
                self._json(200, {"synthetic": True, "leads": store.list()})
            elif self.path == "/api/demo/scorecard":
                self._json(200, aggregate_synthetic_scorecard(store.list()))
            elif self.path.startswith("/api/demo/scenarios/"):
                parts = self.path[len("/api/demo/scenarios/"):].split("/")
                if (len(parts) != 2 or DEMO_REF.fullmatch(parts[0]) is None
                        or parts[1] not in SCENARIOS):
                    self._json(404, {"error": "Unknown synthetic scenario"})
                    return
                lead = store.get(parts[0])
                if lead is None:
                    self._json(404, {"error": "Unknown synthetic reference"})
                    return
                self._json(200, {"synthetic": True,
                                 "scenario": simulate_evidence_path(lead, parts[1])})
            elif self.path.startswith("/api/demo/recovery/"):
                ref = self.path[len("/api/demo/recovery/"):]
                if DEMO_REF.fullmatch(ref) is None:
                    self._json(404, {"error": "Unknown synthetic reference"})
                    return
                lead = store.get(ref)
                if lead is None:
                    self._json(404, {"error": "Unknown synthetic reference"})
                    return
                self._json(200, {"synthetic": True, "preview": build_recovery_preview(lead)})
            elif self.path in ("/", "/demo"):
                self.send_response(302)
                self.send_header("Location", "/demo/")
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
            elif self.path in assets:
                filename, mime = assets[self.path]
                try:
                    raw = (web_dir / filename).read_bytes()
                except OSError:
                    self._json(404, {"error": "Demo asset unavailable"})
                    return
                if len(raw) > 512_000:
                    self._json(413, {"error": "Demo asset too large"})
                    return
                self._write(200, raw, mime)
            else:
                self._json(404, {"error": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            if not self._valid_host():
                self._json(403, {"error": "Loopback host required"})
                return
            if self.path != "/api/demo/leads":
                self._json(404, {"error": "Not found"})
                return
            origin = self.headers.get("Origin")
            if origin is not None and origin.lower() != "http://" + self.headers["Host"].lower():
                self._json(403, {"error": "Cross-origin demo writes blocked"})
                return
            if self.headers.get_content_type() != "application/json":
                self._json(415, {"error": "JSON content type required"})
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 <= length <= MAX_BODY_BYTES:
                    self._json(413, {"error": "Invalid or oversized request"})
                    return
                incoming = json.loads(self.rfile.read(length))
                row, created = store.add(incoming)
            except LeadConflictError as exc:
                self._json(409, {"error": str(exc)})
                return
            except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)[:200]})
                return
            self._json(201 if created else 200, {"lead": row, "created": created})

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Local synthetic-only RRE prototype")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Port must be 1..65535")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(DemoStore()))
    print(f"Synthetic-only RRE demo: http://127.0.0.1:{args.port}/health", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
