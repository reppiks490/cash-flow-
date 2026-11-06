"""Reproducible local-only synthetic HTTP acceptance smoke.

Run: PYTHONPATH=products/revenue_recovery python -m backend.smoke
No real records, contacts, credentials, external requests, or network services.
"""
from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


def run_smoke() -> dict:
    """Exercise the integrated HTTP path on an ephemeral 127.0.0.1 port."""
    store = DemoStore()
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    checks: list[str] = []

    def fetch(method: str, path: str, payload: str | None = None) -> tuple[int, dict]:
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_port, timeout=3
        )
        try:
            headers = {"Content-Type": "application/json"} if payload is not None else {}
            connection.request(method, path, body=payload, headers=headers)
            response = connection.getresponse()
            data = json.loads(response.read())
            return response.status, data
        finally:
            connection.close()

    def check(condition: bool, label: str) -> None:
        if not condition:
            raise RuntimeError("Synthetic smoke failed: " + label)
        checks.append(label)

    lead = (
        '{"synthetic":true,"external_ref":"QA-SMOKE-001",'
        '"source":"website","need":"repair"}'
    )
    try:
        code, data = fetch("GET", "/health")
        check(code == 200 and data.get("synthetic_only") is True, "health")

        code, data = fetch("POST", "/api/demo/leads", lead)
        check(code == 201 and data.get("created") is True, "synthetic intake")

        code, data = fetch("POST", "/api/demo/leads", lead)
        check(code == 200 and data.get("created") is False, "idempotent replay")

        ambiguous = (
            '{"synthetic":false,"synthetic":true,'
            '"external_ref":"QA-SMOKE-BAD","source":"website","need":"repair"}'
        )
        code, data = fetch("POST", "/api/demo/leads", ambiguous)
        check(code == 400 and data.get("error") == "Duplicate JSON field",
              "ambiguous JSON rejected")

        code, data = fetch("GET", "/api/demo/leads")
        check(code == 200 and len(data.get("leads", [])) == 1,
              "rejected record not stored")

        code, data = fetch("GET", "/api/demo/recovery/QA-SMOKE-001")
        preview = data.get("preview", {})
        followup = preview.get("followup", {})
        check(code == 200 and preview.get("synthetic") is True
              and followup.get("approved") is False
              and followup.get("transmitted") is False,
              "review-only unsent draft")

        crm = preview.get("crm", {})
        check(crm.get("dry_run") is True and crm.get("transmitted") is False,
              "offline CRM preview")

        code, data = fetch(
            "GET", "/api/demo/scenarios/QA-SMOKE-001/closed_job_mock"
        )
        scene = data.get("scenario", {})
        metrics = scene.get("metrics", {})
        check(code == 200 and metrics.get("mock_closed_jobs") == 1
              and metrics.get("actual_jobs_closed") == 0
              and metrics.get("verified_payment_receipts") == 0
              and all(event.get("external_side_effect") is False
                      for event in scene.get("events", [])),
              "mock closure is never a verified sale")

        code, data = fetch(
            "GET", "/api/demo/policy/QA-SMOKE-001/revoked_mock"
        )
        policy = data.get("policy", {})
        check(code == 200 and policy.get("suppressed") is True
              and policy.get("draft") is None
              and policy.get("may_contact_real_person") is False,
              "revocation suppresses draft")

        code, data = fetch("GET", "/api/demo/scorecard")
        counts, verified = data.get("counts", {}), data.get("verified", {})
        check(code == 200 and counts.get("received_demo_leads") == 1
              and counts.get("real_customers") is None
              and verified.get("payment_receipts") == 0
              and verified.get("rre_monthly_profit_cents") == 0,
              "unverified revenue and profit not inferred")

        code, _ = fetch("POST", "/api/send", "{}")
        check(code == 404, "no outbound send API")

        code, _ = fetch("POST", "/api/billing", "{}")
        check(code == 404, "no billing API")

        return {
            "status": "pass",
            "synthetic": True,
            "checks_passed": len(checks),
            "checks": checks,
            "real_outreach_enabled": False,
            "verified_receipts": 0,
            "production_readiness": False,
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def main() -> None:
    try:
        result = run_smoke()
    except (AssertionError, RuntimeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "fail", "synthetic": True,
                          "error": str(exc)}))
        raise SystemExit(1) from exc
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
