import unittest

from moneyfall.launch import make_packet


class OutreachBrandingTests(unittest.TestCase):
    def profile(self):
        return dict(
            sender_name="Example Owner",
            sender_email="owner@example.com",
            postal_address="123 Example St, Example, WA 00000",
            payment_url="https://buy.stripe.com/example",
            payment_verified=True,
        )

    def prospect(self):
        return dict(
            id="one",
            company="Example Agency",
            recipient="hello@example.org",
            recipient_source="https://example.org/contact",
            contact_verified=True,
            evidence_url="https://example.org/services",
            evidence="Publishes content marketing services",
            offer="white-label-content",
            fit_reviewed=True,
            proof_path="proof.pdf",
            proof_sha256="a" * 64,
        )

    def test_explicit_brand_identifies_new_outreach(self):
        profile = self.profile()
        profile["brand"] = "  Vellumflare Studio  "
        packet = make_packet(profile, self.prospect(), intro="Hello")

        self.assertEqual(packet["brand"], "Vellumflare Studio")
        self.assertEqual(packet["subject"], "Vellumflare Studio — an original content pilot for Example Agency")
        self.assertIn("\nExample Owner\nVellumflare Studio\nCommercial offer.", packet["body"])

    def test_omitted_brand_preserves_legacy_packet_shape_and_copy(self):
        packet = make_packet(self.profile(), self.prospect(), intro="Hello")

        self.assertNotIn("brand", packet)
        self.assertEqual(packet["subject"], "An original content pilot for Example Agency")
        self.assertIn("\nExample Owner\nCommercial offer.", packet["body"])
        self.assertNotIn("Vellumflare Studio", packet["body"])

    def test_invalid_explicit_brand_is_rejected(self):
        for brand in ("", "   ", "Vellumflare\nBcc: x@example.com", "x" * 65, 123):
            with self.subTest(brand=brand):
                profile = self.profile()
                profile["brand"] = brand
                with self.assertRaises(ValueError):
                    make_packet(profile, self.prospect(), intro="Hello")


if __name__ == "__main__":
    unittest.main()
