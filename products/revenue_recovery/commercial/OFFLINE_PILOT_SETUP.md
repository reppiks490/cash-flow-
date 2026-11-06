# Offline HVAC pilot-plan preflight (synthetic only)

**Status:** engineering demo. This is not live customer onboarding, a paid
subscription, a connected integration, an actual appointment, or pilot approval.

Commercial ticket: [RRE-04 #26](https://github.com/reppiks490/cash-flow-/issues/26).
Stacked after [commercial PR #43](https://github.com/reppiks490/cash-flow-/pull/43).
Coordinate backend API/tenant contracts through [RRE-01 #23](https://github.com/reppiks490/cash-flow-/issues/23).

## Scope

`commercial.offline_pilot.build_offline_pilot_plan` accepts only a validated
`demo-*` workspace, the existing five literal demo-readiness booleans, and
three mock/disabled port choices (CRM, email draft, calendar). It returns
JSON-serializable **preview configuration**, not connector objects. There are no
credentials, network calls, writes, actual sends, bookings or charges.

`mock` means only that future, separate in-memory demo adapters could be
previewed. It does **not** mean a vendor connection or authorized automation.
`disabled` removes even preview availability. Both modes keep
`connected=false` and `live_read_enabled=false` /
`live_write_enabled=false`.

`demo_readiness=offline_demo_ready` establishes only that the five synthetic
operator checks are true. Even then:
- `pilot_ready=false`
- `human_review_required=true`
- all live onboarding, outreach, CRM writes, bookings and billing are disabled;
- verified customer counts, receipts and monthly net profit remain unknown
  (`null`), never inferred from the hypothetical quote.

No function accepts customer contact data, provider credentials, real business
records, billing tokens, opt-in attestations, or a deployment flag. The quote
parser accepts only plain positive USD decimal **strings** from $0.01 through
$10,000.00, with at most two decimal places. The bound is an engineering input
limit, not a validated market price. Existing $700/month positioning remains
an **unvalidated commercial hypothesis**.

## Local-only demonstration

From the repository root:

```bash
PYTHONPATH=products/revenue_recovery python -m unittest commercial.test_offline_pilot -v
```

On PowerShell:

```powershell
$env:PYTHONPATH = "products/revenue_recovery"
python -m unittest commercial.test_offline_pilot -v
```

Illustrative use in a local Python interpreter after setting the PYTHONPATH:

```python
from commercial.demo_readiness import REQUIRED_CHECKS
from commercial.offline_pilot import build_offline_pilot_plan

workspace = {
    "workspace_id": "demo-hvac-001",
    "industry": "hvac",
    "synthetic": True,
    "consent_mode": "manual_review_only",
}
checks = {key: True for key in REQUIRED_CHECKS}
plan = build_offline_pilot_plan(workspace, checks)
assert plan["demo_readiness"] == "offline_demo_ready"
assert plan["billing_enabled"] is False
assert plan["pilot_ready"] is False
```

## Boundaries to production

This standalone commercial preflight is intentionally **not wired into
`backend/app.py`**. Principal Architect and QA must review API contracts,
authentication, tenant authorization, private storage, meaningful consent
proof, suppressions, idempotency, event auditing, and human approval before
even a controlled pilot is considered. A mock port cannot be promoted into
a live provider by toggling these fields; that would require a separate
authorized integration with security, compliance, and operational review.

No real outreach, customer import, actual billing, production deployment or
external provider calls are permitted by this work.
