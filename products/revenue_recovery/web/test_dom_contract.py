"""Run the dependency-free Node DOM regression suite in product Python CI.

The existing RRE workflow discovers test_*.py but does not independently
execute *.test.cjs files. This bridge makes PR #42's DOM checks mandatory.
No browser network, external service, PII or paid dependency is used.
"""
from pathlib import Path
import subprocess
import unittest


class DashboardDOMContractTests(unittest.TestCase):
    def test_node_dom_contract(self):
        contract = Path(__file__).with_name("dom_contract.test.cjs")
        self.assertTrue(contract.is_file(), "Node dashboard contract file is missing")
        try:
            result = subprocess.run(
                ["node", "--test", str(contract)],
                cwd=contract.parent,
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except FileNotFoundError as exc:
            self.fail("Node.js is required to validate the dashboard DOM suite: " + str(exc))
        except subprocess.TimeoutExpired:
            self.fail("Dashboard DOM contract timed out after 20 seconds")
        self.assertEqual(
            result.returncode, 0,
            "Node DOM contract failed:\n" + result.stdout + "\n" + result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
