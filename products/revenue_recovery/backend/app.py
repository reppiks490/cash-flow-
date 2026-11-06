"""Local-only, synthetic-lead HTTP prototype for Revenue Recovery Engine.

No customer information, outbound messaging, paid API calls or persistence are
supported. This process is deliberately unsuitable for public deployment.
"""

from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MAX_BODY_BYTES = 16_384
MAX_LEADS = 2_000


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
        row = {
            "synthetic": True,
            "external_ref": external_ref,
            "source": incoming["source"].strip(),
            "need": incoming["need"].strip(),
            "status": "received",
        }
        with self._lock:
            if external_ref in self._leads:
                return dict(self._leads[external_ref]), False
            if len(self._leads) >= MAX_LEADS:
                raise ValueError("Demo capacity reached")
            self._leads[external_ref] = row
            return dict(row), True

    def list(self) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self._leads.values()]


def make_handler(store: DemoStore):
    class Handler(BaseHTTPRequestHandler):
        server_version = "RRE-Demo/0.1"

        def _json(self, code: int, data: dict) -> None:
            raw = json.dumps(data, sort_keys=True).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/health":
                self._json(200, {"service": "revenue-recovery-demo", "status": "ok", "synthetic_only": True})
            elif self.path == "/api/demo/leads":
                self._json(200, {"synthetic": True, "leads": store.list()})
            else:
                self._json(404, {"error": "Not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/api/demo/leads":
                self._json(404, {"error": "Not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "-1"))
                if not 0 <= length <= MAX_BODY_BYTES:
                    self._json(413, {"error": "Invalid or oversized request"})
                    return
                incoming = json.loads(self.rfile.read(length))
                row, created = store.add(incoming)
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
