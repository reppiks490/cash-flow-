"""Principal-owned CLI smoke regression; fully local synthetic fixture."""
import unittest

from backend.smoke import run_smoke


class SyntheticPipelineSmokeTests(unittest.TestCase):
    def test_complete_local_pipeline_is_fail_closed(self):
        result = run_smoke()
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["synthetic"])
        self.assertEqual(result["checks_passed"], 12)
        self.assertFalse(result["real_outreach_enabled"])
        self.assertEqual(result["verified_receipts"], 0)
        self.assertFalse(result["production_readiness"])
        self.assertIn("revocation suppresses draft", result["checks"])
        self.assertIn("no billing API", result["checks"])


if __name__ == "__main__":
    unittest.main()
