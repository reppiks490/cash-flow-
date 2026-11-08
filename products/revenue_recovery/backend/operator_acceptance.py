"""Synthetic-only local HTTP acceptance; no third-party network or customer data.

Run: PYTHONPATH=products/revenue_recovery python -m backend.operator_acceptance
"""
from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


def require(condition: bool, detail: str) -> None:
    """Raise even under python -O; acceptance must never silently pass."""
    if not condition:
        raise RuntimeError(f"Operator acceptance failed: {detail}")


def run_acceptance() -> None:
    store = DemoStore()
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    port = server.server_port

    def request(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
        conn = HTTPConnection("127.0.0.1", port, timeout=5)
        payload = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Host": f"127.0.0.1:{port}"}
        if payload is not None:
            headers["Content-Type"] = "application/json"
        try:
            conn.request(method, path, body=payload, headers=headers)
            response = conn.getresponse()
            return response.status, json.loads(response.read().decode("utf-8"))
        finally:
            conn.close()

    try:
        lead = {"synthetic": True, "external_ref": "QA-OPERATOR-01",
                "source": "website", "need": "AC not cooling"}
        status, health = request("GET", "/health")
        require(status == 200 and health["synthetic_only"] is True, "HTTP assertion 1 failed")
        status, created = request("POST", "/api/demo/leads", lead)
        require(status == 201 and created["created"] is True, "HTTP assertion 2 failed")
        status, replay = request("POST", "/api/demo/leads", lead)
        require(status == 200 and replay["created"] is False, "HTTP assertion 3 failed")
        status, conflict = request("POST", "/api/demo/leads", {**lead, "need": "heating issue"})
        require(status == 409, f"HTTP assertion 4 failed: {status}, {conflict}")
        status, preview = request("GET", "/api/demo/recovery/QA-OPERATOR-01")
        require(status == 200 and preview["synthetic"] is True, "HTTP assertion 5 failed")
        result = preview["preview"]
        require(result["qualification"]["consent_verified"] is False, "HTTP assertion 6 failed")
        require(result["followup"]["approved"] is False, "HTTP assertion 7 failed")
        require(result["followup"]["transmitted"] is False, "HTTP assertion 8 failed")
        require(result["crm"]["transmitted"] is False, "HTTP assertion 9 failed")
        require(result["appointment"]["confirmed"] is False, "HTTP assertion 10 failed")
        require(result["attribution"]["verified_payment_receipts"] == 0, "HTTP assertion 11 failed")
        status, scenario = request("GET", "/api/demo/scenarios/QA-OPERATOR-01/closed_job_mock")
        require(status == 200 and scenario["synthetic"] is True, "HTTP assertion 12 failed")
        require(scenario["scenario"]["metrics"]["actual_messages_sent"] == 0, "HTTP assertion 13 failed")
        require(scenario["scenario"]["metrics"]["verified_payment_receipts"] == 0, "HTTP assertion 14 failed")
        status, scorecard = request("GET", "/api/demo/scorecard")
        require(status == 200 and scorecard["synthetic"] is True, "HTTP assertion 15 failed")
        require(scorecard["verified"]["payment_receipts"] == 0, "HTTP assertion 16 failed")
        status, blocked = request("POST", "/api/demo/payments", {"synthetic": True})
        require(status == 404, f"HTTP assertion 17 failed: {status}, {blocked}")
        status, leads = request("GET", "/api/demo/leads")
        require(status == 200 and len(leads["leads"]) == 1, "HTTP assertion 18 failed")
        print("PASS: local synthetic HTTP operator acceptance; no external calls")
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


if __name__ == "__main__":
    run_acceptance()
