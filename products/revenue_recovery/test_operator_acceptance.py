"""Run the principal-owned synthetic HTTP acceptance in existing unittest discovery.

No vendor access, real customer records, outreach, or production operations.
"""
from __future__ import annotations

import unittest

from backend.operator_acceptance import run_acceptance


class OperatorHTTPAcceptanceTests(unittest.TestCase):
    def test_local_synthetic_http_workflow(self) -> None:
        # run_acceptance uses explicit require(), so checks also survive python -O.
        run_acceptance()


if __name__ == "__main__":
    unittest.main()
