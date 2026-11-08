"""Synthetic-only local HTTP acceptance; no third-party network or customer data.

Run: PYTHONPATH=products/revenue_recovery python -m backend.operator_acceptance
"""
from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from backend.app import DemoStore, make_handler


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
        assert status == 200 and health["synthetic_only"] is True
        status, created = request("POST", "/api/demo/leads", lead)
        assert status == 201 and created["created"] is True
        status, replay = request("POST", "/api/demo/leads", lead)
        assert status == 200 and replay["created"] is False
        status, conflict = request("POST", "/api/demo/leads", {**lead, "need": "heating issue"})
        assert status == 409, (status, conflict)
        status, preview = request("GET", "/api/demo/recovery/QA-OPERATOR-01")
        assert status == 200 and preview["synthetic"] is True
        result = preview["preview"]
        assert result["qualification"]["consent_verified"] is False
        assert result["followup"]["approved"] is False
        assert result["followup"]["transmitted"] is False
        assert result["crm"]["transmitted"] is False
        assert result["appointment"]["confirmed"] is False
        assert result["attribution"]["verified_payment_receipts"] == 0
        status, scenario = request("GET", "/api/demo/scenarios/QA-OPERATOR-01/closed_job_mock")
        assert status == 200 and scenario["synthetic"] is True
        assert scenario["scenario"]["metrics"]["actual_messages_sent"] == 0
        assert scenario["scenario"]["metrics"]["verified_payment_receipts"] == 0
        status, scorecard = request("GET", "/api/demo/scorecard")
        assert status == 200 and scorecard["synthetic"] is True
        assert scorecard["verified"]["payment_receipts"] == 0
        status, blocked = request("POST", "/api/demo/payments", {"synthetic": True})
        assert status == 404, (status, blocked)
        status, leads = request("GET", "/api/demo/leads")
        assert status == 200 and len(leads["leads"]) == 1
        print("PASS: local synthetic HTTP operator acceptance; no external calls")
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)


if __name__ == "__main__":
    run_acceptance()
