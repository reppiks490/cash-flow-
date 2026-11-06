# RRE-04 — Operator-safe HVAC sales demo packet (synthetic only)

**Status:** internal proposal, not an approved sales claim or executed pilot. **No customer discovery, outreach, real-data import, public hosting, booking, billing or deployment is authorized.** This packet describes a working *local synthetic prototype*, not verified demand, ROI, tenant safety or market readiness. Use with [PILOT_OFFER_AND_DISCOVERY.md](PILOT_OFFER_AND_DISCOVERY.md), [COMPETITOR_EVIDENCE.md](COMPETITOR_EVIDENCE.md) and [MEASUREMENT_PROTOCOL.md](MEASUREMENT_PROTOCOL.md).

## Who this is for / the proposition to falsify

**Hypothesis:** an owner-operated HVAC contractor already receiving calls, web requests and estimates may value an *operator-supervised leakage audit* that identifies missed follow-up or unexplained pipeline stages **after** checking whether their existing CRM already solves it. RRE is not a substitute for Jobber/Housecall Pro/ServiceTitan or an autonomous texting service. The proposed $700/month managed-support price is **unvalidated**, negotiable only after private, authorized buyer research. There are no paying customers or verified saved jobs in the present evidence.

### 12-minute demonstration: local machine only

| Minute | Operator action | What can legitimately be said | What must NOT be claimed |
|---|---|---|---|
| 0–1 | State that every displayed record is synthetic and external systems are disconnected. | This shows the demonstration workflow. | Real customer onboarding, production readiness, compliance clearance. |
| 1–3 | Run the local loopback-only demo from `RUNBOOK_LOCAL.md` and load bundled HVAC example leads in `/demo/`. | Enumerated, synthetic intake and duplicate/conflict rejection are testable. | PII-safe live intake or customer import. |
| 3–5 | Select a fixture; show rubric source, missing evidence and review-only follow-up draft. | Local deterministic qualification and **unsent** draft. | Real AI vendor invocation, consent, customer messages, or sent email. |
| 5–7 | Show dry-run CRM preview, mock appointment and closed-job timeline. | Previewed actions with no provider writes or bookings. | Confirmed appointment, closed job or collected payment. |
| 7–9 | Show synthetic scorecard and open hypothetical economics. | All actual receipts/net profit are unverified; modeled numbers are **scenarios**. | Proven conversion lift, revenue recovery or $2,500/month net. |
| 9–11 | Compare existing CRM's native follow-up settings and discuss an audit gap. | We would recommend using an already-paid-for feature where sufficient. | An unsupported claim that RRE outperforms incumbents. |
| 11–12 | Ask for *permission to propose* a privately reviewed discovery study; do **not** contact anyone. | A later pilot would need distinct legal/security/operator approvals. | Any commitment, invitation, email, SLA or billing activation. |

**No-cost local commands** from repo root, Python 3.11+:

```bash
PYTHONPATH=products/revenue_recovery python -m unittest discover -s products/revenue_recovery -p 'test_*.py' -v
PYTHONPATH=products/revenue_recovery python -m commercial.demo_cli
PYTHONPATH=products/revenue_recovery python -m backend.app --port 8765
```

Open `http://127.0.0.1:8765/demo/` **only on the same computer**. The default CLI returns a *blocked* demo-readiness plan; it does not provision an account. For the detailed PowerShell/Git Bash procedure and limits, use [RUNBOOK_LOCAL.md](../RUNBOOK_LOCAL.md). Never expose the unauthenticated demo on LAN, 5G tunnel or public IP.

## Buyer objection handling (for an authorized future discussion only)

- **"My Jobber plan sends quote reminders."** Agree; Jobber documents native automated quote email/text follow-up. First inspect whether existing automation, permissions and staff queue resolve the issue. **Do not sell duplication.**
- **"Hatch already handles this."** Hatch markets integrated multichannel follow-up and reporting. Ask what *specific, independently observed* audit/provenance or manual-approval gap remains. Its case-study results are **vendor claims**, not RRE performance evidence.
- **"Why would I pay $700 monthly?"** That is an unvalidated managed-service hypothesis. Buyer-side *hypothetical* sensitivity: $700 / $250 contribution per genuinely incremental paid job requires **3 incremental paid jobs** to offset the fee; separately $700 / $50 loaded labor hour corresponds to **14 staff-hours of opportunity cost**. These are **alternative comparisons**, never additive ROI; neither jobs nor staff savings has been verified, and recovered time is not necessarily payroll cash savings.
- **"Can you text my customers automatically?"** **No.** Mock drafts cannot be sent; lawful consent, suppression, provider agreements, operator identity and explicit approval are unresolved.
- **"How much extra money does it make?"** **Unknown.** Neither synthetic closed jobs nor estimates are authenticated settled receipts. The business's recovered collections and RRE's own subscription profit are distinct.

## Evidence labels a presenter must display

| Claim type | Current evidence classification | Source required for an upgraded claim |
|---|---|---|
| Demo leads / unsent drafts / mock bookings | Synthetic offline fixture | None; never promote fixture to real outcome |
| Contractor appointment / closed job | **Unverified** | Authenticated source event plus consented tenant-specific audit |
| Contractor collections / recovered revenue | **Unverified** | Settled unique receipt, refund reconciliation, baseline attribution |
| RRE paid customer count / recurring collections | **Unverified** | Private signed contracts, processor settlement, cancellation and refunds |
| RRE recurring net profit | **Unverified** | Reconciled settled revenue **minus** all allocated variable/fixed costs, support/owner labor, acquisition, refunds, fees and documented tax basis |
| Proposed 30-day pilot and $700 price | Unvalidated commercial hypothesis | Privately authorized interviews, signed scope/terms and observed costs |
| Live pilot or production readiness | **Not established** | Security, authenticated tenants, vendor/legal signoff, audited outbound controls and owner authorization |

## Pilot decision rubric (NOT an active recruitment program)

A future owner-approved interview should explicitly test: existing CRM/plan/automation; evidence of unresolved missed-inquiry or stale-estimate exceptions; employee review time; source of truth for sends, appointments and settled payments; suppression/consent flow; secure integration rights; willingness to pay *relative to alternatives*; and contract cancellation constraints. **Capture no business names, contacts or identifiable records in public GitHub.** Predefine denominators/time window and count a missing event as **unknown**, not as a zero-conversion event. Require reviewer signoff before claiming even a pilot result.

**Stop / pivot criteria:** if a contractor's incumbent workflow already closes the evidenced gap, recommend configuring it instead. If no independently documented gap or credible willingness-to-pay appears, reject the $700 premise rather than promote modeled outcomes as proof. Do not solicit interviewees without a separate owner authorization and legal/channel review.

## Primary-source research register (2026-11-06)

- Jobber Help Center, *Automations* (updated 2026): native quote follow-up and communication preferences. https://help.getjobber.com/en/articles/automations/
- Jobber, *Quotes*: quote reminders and approvals already offered; vendor marketing claims are not independent outcomes. https://www.getjobber.com/features/quotes/
- Hatch, *TurnPoint case study*: advertises large-scale quote follow-up and reports; single vendor case study is not independent validation for RRE. https://www.usehatchapp.com/case-studies/turnpoint-services
- US FTC, *CAN-SPAM Act: A Compliance Guide for Business*: federal commercial-email obligations apply to B2B email; human review alone is not compliance. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

**No compliance opinion:** Rules differ by channel, message purpose and jurisdiction. Obtain qualified legal review of CAN-SPAM, TCPA, state privacy/marketing rules, vendor terms and suppression handling before authorizing any outreach. No live service-level, cancellation, refund or security terms have been accepted.
