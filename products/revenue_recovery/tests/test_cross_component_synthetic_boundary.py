"""Cross-component fail-closed contracts for the local synthetic HVAC demo.

No live providers, network calls, PII, or financial transactions.
"""
import unittest

from backend.crm import preview_crm_envelope
from backend.onboarding import (
    OnboardingError, activate_billing, draft_subscription_quote,
    prepare_demo_workspace, send_followup,
)


WORKSPACE = {
    "workspace_id": "demo-hvac_qa",
    "industry": "hvac",
    "synthetic": True,
    "consent_mode": "manual_review_only",
}
LEAD = {
    "synthetic": True,
    "external_ref": "DEMO-HVAC-001",
    "source": "website",
    "need": "AC not cooling",
    "status": "received",
}


class SyntheticBoundaryTests(unittest.TestCase):
    def test_workspace_and_crm_preview_cannot_claim_live_operations(self):
        workspace = prepare_demo_workspace(dict(WORKSPACE))
        envelope = preview_crm_envelope(dict(LEAD))
        self.assertTrue(workspace.synthetic)
        self.assertEqual(workspace.billing_status, "disabled")
        self.assertEqual(workspace.consent_mode, "manual_review_only")
        self.assertTrue(envelope["synthetic"])
        self.assertTrue(envelope["dry_run"])
        self.assertFalse(envelope["transmitted"])
        self.assertFalse(envelope["appointment_confirmed"])
        self.assertIsNone(envelope["provider"])
        self.assertIsNone(envelope["provider_record_id"])
        self.assertEqual(envelope["verified_recovered_revenue_cents"], 0)

    def test_customer_contact_fields_fail_closed_at_both_boundaries(self):
        for field in ("email", "phone", "customer_name", "api_key", "tenant_id"):
            with self.subTest(field=field):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**WORKSPACE, field: "not-real"})
                with self.assertRaises(ValueError):
                    preview_crm_envelope({**LEAD, field: "not-real"})

    def test_fabricated_paid_and_booked_status_never_become_crm_evidence(self):
        for status in ("paid", "booked", "closed_won"):
            with self.subTest(status=status):
                with self.assertRaises(ValueError):
                    preview_crm_envelope({**LEAD, "status": status})

    def test_consent_and_synthetic_escalation_denied(self):
        for change in (
            {"synthetic": False},
            {"consent_mode": "auto_send"},
            {"industry": "other"},
        ):
            with self.subTest(change=change):
                with self.assertRaises(OnboardingError):
                    prepare_demo_workspace({**WORKSPACE, **change})
        with self.assertRaises(ValueError):
            preview_crm_envelope({**LEAD, "synthetic": False})

    def test_quote_does_not_create_receipt_or_enable_outbound(self):
        quote = draft_subscription_quote("700.00")
        self.assertTrue(quote["synthetic"])
        self.assertTrue(quote["nonbinding"])
        self.assertEqual(quote["billing_status"], "disabled")
        self.assertIsNone(quote["invoice_id"])
        self.assertIsNone(quote["payment_receipt"])
        self.assertFalse(quote["send_enabled"])

    def test_live_side_effects_denied_even_with_approval_shaped_kwargs(self):
        with self.assertRaises(PermissionError):
            activate_billing(owner_approved=True, receipt="DEMO-RECEIPT")
        with self.assertRaises(PermissionError):
            send_followup(approved=True, consent=True)


if __name__ == "__main__":
    unittest.main()
