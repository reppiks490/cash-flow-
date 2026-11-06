"""Single source of truth for public synthetic-only input vocabulary.

These demo-only categories intentionally contain no freeform customer data.
This module does not establish production privacy, authorization or tenancy.
"""
from __future__ import annotations

import re

SOURCES = frozenset({"demo", "website", "phone", "referral"})
NEEDS = frozenset({"AC not cooling", "AC maintenance", "repair",
                   "maintenance", "estimate follow-up", "heating issue"})
REF = re.compile(r"(?:DEMO|QA)[-_][A-Za-z0-9_-]{1,56}\Z", re.IGNORECASE | re.ASCII)
