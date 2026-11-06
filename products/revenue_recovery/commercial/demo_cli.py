"""Local, synthetic-only self-serve demo preflight.

This CLI prints a plan. It never imports a provider SDK, reads credentials,
stores customer data, sends messages, books jobs or charges a card.
"""
from __future__ import annotations

import argparse
import json
import sys

from backend.onboarding import OnboardingError
from commercial.demo_readiness import REQUIRED_CHECKS
from commercial.offline_pilot import build_offline_pilot_plan


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print an offline HVAC demo setup plan; NO live integrations or customer onboarding."
    )
    parser.add_argument("--workspace-id", default="demo-hvac-001")
    parser.add_argument(
        "--check", action="append", default=[], metavar="REVIEWED_CHECK",
        help="Repeat for each reviewed synthetic demo check; missing checks block readiness.",
    )
    parser.add_argument("--crm-port", default="mock", metavar="mock|disabled")
    parser.add_argument("--email-port", default="mock", metavar="mock|disabled")
    parser.add_argument("--calendar-port", default="mock", metavar="mock|disabled")
    parser.add_argument("--monthly-price", default="700.00", metavar="USD")
    args = parser.parse_args(argv)

    # Never allow unchecked or invented checklist labels to be treated as approval.
    if any(name not in REQUIRED_CHECKS for name in args.check):
        print("Rejected: unknown synthetic demo checklist item", file=sys.stderr)
        return 2

    workspace = {
        "workspace_id": args.workspace_id,
        "industry": "hvac",
        "synthetic": True,
        "consent_mode": "manual_review_only",
    }
    checks = {name: name in args.check for name in REQUIRED_CHECKS}
    try:
        plan = build_offline_pilot_plan(
            workspace, checks,
            crm_port=args.crm_port,
            email_port=args.email_port,
            calendar_port=args.calendar_port,
            monthly_price_usd=args.monthly_price,
        )
    except OnboardingError:
        # Avoid printing user-supplied input, which may accidentally contain PII.
        print("Rejected: invalid synthetic-only onboarding or pricing input", file=sys.stderr)
        return 2

    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
