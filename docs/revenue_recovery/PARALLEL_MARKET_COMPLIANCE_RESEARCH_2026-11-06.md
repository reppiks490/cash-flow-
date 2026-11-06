# RRE evidence-backed market and compliance review — 2026-11-06

**Source:** Parallel Search of publicly published primary source pages (vendor documentation, FCC and FTC). **Status:** exploratory product research, not legal advice, proven customer demand, verified pricing, compliance certification or permission to contact anyone. No outside data was imported into RRE; no emails/texts/calls were sent.

## Competitive reality: eliminate non-differentiated features

| Vendor / source | Vendor-supported behavior observed | RRE implication |
|---|---|---|
| Jobber — https://www.getjobber.com/features and https://www.getjobber.com/pricing | Quote follow-up and invoice reminders are marketed capabilities; plan, add-ons and billing cadence matter. | Do not sell basic reminder automation as an exclusive feature or price it as if operators have no alternatives. |
| Hatch — https://www.usehatchapp.com/integrations/jobber and https://www.usehatchapp.com/solutions/estimate-follow-up | CRM integration, lead reactivation, estimate follow-up and AI communication are marketed. The Jobber integration page was dated 2026-09-28 when reviewed. | Generic AI CSR messaging is a competing category; avoid promising novel AI capability without a verified edge. |
| Housecall Pro — https://help.housecallpro.com/en/articles/12119814-automate-job-creation-from-approved-estimates | Approved-estimate-to-job automation is described as included with plans, though apparently off until enabled. | An operator might need setup/audit work rather than a new recurring SaaS subscription. |
| ServiceTitan — incumbent feature comparison not revalidated in this cycle | Existing integration evidence and competition must be checked against current plan and actual customer's entitlements, not assumed. | No broad claims of competitor inferiority or unvalidated ROI. |

These are vendor claims rather than independently tested outcomes. Pages may change; obtain a current quote and confirm the exact CRM tier when a prospective customer authorizes discovery.

### Narrow value proposition to test, not promise

**Exception audit and operator-controlled recovery orchestration** across tools the HVAC operator already pays for: identify where a lead or estimate fell outside incumbent follow-up automations, show source evidence and suppression gaps, recommend a staff action, verify whether a booking and *settled* payment eventually occurred, and quantify costs. Never infer cash from a quote, send, appointment or closed-job flag.

A paid monthly managed service at the earlier **$700 hypothetical price** is only credible if a user documents incremental workflow value beyond incumbent features and full operating costs. Seek qualitative discovery before any price or revenue promise; pitch configured existing features if those solve the problem.

### Falsification interview (no outreach authorization)

Ask actual operators *with owner permission* which CRM and tier they use; whether follow-ups are already enabled; where handoffs fail; what duplicate or opted-out lead exceptions arise; whether messages are legally permissioned; what share of lost jobs truly reflects preventable gaps; which paid plan could already fix it; who can authenticate job payments; and what specific gap justifies incremental cost. Record objections and no-interests, not just enthusiasts. Existing demo is synthetic, and no buyer interviews have occurred.

## Regulatory guardrails before any outbound automation

- **FCC consumer guidance:** https://www.fcc.gov/consumers/guides/stop-unwanted-robocalls-and-texts (published 2026-02-27 in Parallel result). The FCC describes consent requirements for autodialed calls and robotexts and states that commercial automated texts require written consent, subject to legal distinctions and exceptions. No current RRE consumer consent or sender relationship is verified.
- **FCC revocation guidance:** https://docs.fcc.gov/public/attachments/DOC-400522A1.pdf (release dated 2024-02-15). The FCC describes consumers' right to revoke consent by reasonable means and restrictions on robocalls/robotexts. Exact effective dates, court developments and industry-specific requirements should be rechecked with counsel before implementation; do not substitute a static engineering value for live law.
- **FTC CAN-SPAM guide:** https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . The FTC says CAN-SPAM also applies to business-to-business promotional email and requires compliant identification, postal-address and opt-out procedures. Lawful content and opt-out duties depend on whether a message is commercial versus transactional.

### Engineering gates derived from that research

1. Default every inbound record to **unknown consent** and **no outbound eligibility**. Never equate a lead being present in a CRM with permission to send.
2. Define a documented communications-purpose taxonomy (transactional versus marketing), jurisdiction, sender identity, lawful consent source, time obtained, scope, channel, and opt-out status in a **private authorized production system**. The present public GitHub repo must contain none of those consumer details.
3. Apply suppression and revocation **before** message approval and **again** immediately before any actual send. Do not assume legal timelines are a permission to send while revoked.
4. Require operator authorization, identity, audit events, delivery receipts and complaint/incident handling. Implement role- and tenant-scoped access control and secure secrets/storage before processing real information.
5. Keep demo payloads categorical and explicitly synthetic; prohibit all actual outbound adapters, billing, CRM updates, appointment booking and verified-income claims until separate owner approval and QA/security/legal sign-off.
6. Verify carrier registration, provider rules and applicable state privacy and marketing laws when a real pilot location is known. There is currently no legally reviewed channel or customer to activate.

## Current implementation cross-check

The product's `backend/demo_evidence.py` returns *mock* lifecycle events only, with `source_evidence_verified=false`, `external_side_effect=false`, and `verified_* = 0`. The UI never contacts external communications services. The workflow is a safe illustration of the evidence hierarchy; it is **not** a signed audit ledger, legal-compliance engine, production-grade identity system or payment authenticator.

**No verified paid clients, recovered money, real contacts, payment receipts or operating profit currently exist in this research.**
