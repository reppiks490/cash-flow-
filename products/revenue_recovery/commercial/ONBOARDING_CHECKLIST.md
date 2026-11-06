# Controlled HVAC pilot onboarding checklist

**Current system: synthetic-only. No customer activation or billing is authorized.**

## Before any live onboarding

- [ ] Verify business owner identity and authority to authorize a pilot.
- [ ] Sign a scope, price, cancellation, retention and data-processing agreement.
- [ ] Complete security review for tenant separation, authentication, encryption, access controls and audit logs.
- [ ] Document source of each lead, communication consent, lawful basis, opt-out and suppression handling.
- [ ] Review applicable TCPA, CAN-SPAM, state law, DNC and CRM/email/SMS vendor terms with qualified counsel.
- [ ] Approve only minimum required data fields, private storage, retention limits, and deletion/return workflow.
- [ ] Establish integration scope and obtain credentials through a secret manager, never GitHub.
- [ ] Define a human approval process for every outbound draft and actual-send audit receipt.
- [ ] Establish source-of-truth for appointment confirmations, closed jobs and paid receipts.
- [ ] Set up verified payment destination and signed webhook verification in an authorized private environment.
- [ ] Establish support, incident response, rollback, and customer termination/export process.
- [ ] Obtain explicit owner approval before any live data import, outbound communications, payment activation, or production deployment.

## Safe synthetic demonstration

- [x] Define demo workspace metadata contract in backend/onboarding.py.
- [x] Reject real customer metadata and unexpected fields at demo onboarding boundary.
- [x] Keep outbound and billing functions disabled.
- [ ] Run test suite in an execution environment and attach passing logs.
- [ ] Integrate onboarding contract with backend/API after Principal Architect approves interface.
- [ ] Complete QA sign-off before promoting to pilot-ready.

**Data boundary:** do not upload customer phone numbers, email addresses, names, addresses, contracts, or payment receipts to this public repository.
