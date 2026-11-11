"""Offline HVAC reporting period boundaries; no tenant records or external effects.

Only date-based local reporting windows are supported. The output is an
explicit half-open UTC interval, including DST transitions.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import re

_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z", re.ASCII)
_ZONE = re.compile(r"[A-Za-z][A-Za-z0-9_+.-]*(?:/[A-Za-z0-9_+.-]+)+\Z", re.ASCII)


def reporting_window(start_date: str, end_date: str, timezone_name: str) -> dict[str, str]:
    """Return UTC boundaries for [local start date, local end date).

    Reject malformed dates, arbitrary timezone paths, zero/negative windows,
    and windows longer than 366 days. No timezone inference or fallback.
    """
    if type(start_date) is not str or not _DATE.fullmatch(start_date):
        raise ValueError("start_date must be YYYY-MM-DD")
    if type(end_date) is not str or not _DATE.fullmatch(end_date):
        raise ValueError("end_date must be YYYY-MM-DD")
    if type(timezone_name) is not str or len(timezone_name) > 80 or not _ZONE.fullmatch(timezone_name):
        raise ValueError("An explicit IANA region timezone is required")
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        zone = ZoneInfo(timezone_name)
    except (ValueError, ZoneInfoNotFoundError) as exc:
        raise ValueError("Invalid reporting date or IANA timezone") from exc
    days = (end - start).days
    if not 1 <= days <= 366:
        raise ValueError("Reporting interval must be 1 to 366 days")
    start_utc = datetime.combine(start, time.min, tzinfo=zone).astimezone(timezone.utc)
    end_utc = datetime.combine(end, time.min, tzinfo=zone).astimezone(timezone.utc)
    if end_utc <= start_utc:
        raise ValueError("Invalid UTC reporting interval")
    return {
        "classification": "reporting_window_only_not_revenue_evidence",
        "timezone": timezone_name,
        "start_local_date": start_date,
        "end_local_date_exclusive": end_date,
        "start_utc_inclusive": start_utc.isoformat(),
        "end_utc_exclusive": end_utc.isoformat(),
    }
