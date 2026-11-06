# Revenue Recovery — responsive synthetic dashboard

This is a static HTML/CSS/JavaScript operator preview with no build tools, third-party scripts, trackers, cookies, authentication bypass or outbound actions. **Not production-ready.**

To preview without a backend, open `index.html` in a browser. It falls back to three explicitly synthetic HVAC fixture records. The status banner distinguishes fixtures from a live local demo API.

To preview via an HTTP server, from `products/revenue_recovery/web` run `python -m http.server 8766 --bind 127.0.0.1`, then visit `http://127.0.0.1:8766`. The local server cannot proxy `/api/demo/leads`, so fixture mode is expected.

The Principal Architect's branch `feature/rre-synthetic-bootstrap-20261106` defines `GET /api/demo/leads` and the lead shape. Once integrated, the Principal Architect can serve these static files from the same loopback origin as the API, avoiding CORS. This branch deliberately does **not** modify backend HTTP routes, which belong to RRE-01.

The dashboard offers lead rows, local unsent follow-up draft preview and a clear accounting integrity panel. The metrics labeled confirmed appointments and verified recovered revenue remain zero until authenticated sources exist. The draft copy action writes only to the user's clipboard.

`backend/crm.py` defines a pure synthetic-only CRM mapping preview; it never sends data, creates appointments, or writes CRM records.

## Verification

Use `PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery/web -p 'test_*.py' -v` from repo root. No live service, payment provider or CRM connection is needed. This UI still requires an authenticated, tenant-safe backend and security review before production use.
