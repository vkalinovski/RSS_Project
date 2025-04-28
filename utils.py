# -*- coding: utf-8 -*-
import datetime as dt

def now_utc() -> str:
    """Текущее время UTC в формате YYYY-MM-DD HH:MM:SS"""
    return dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def normalise_date(date_str: str | None) -> str:
    """Приводим даты публикации к формату YYYY-MM-DD"""
    if not date_str:
        return dt.datetime.utcnow().strftime("%Y-%m-%d")
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(date_str[:25], fmt).strftime("%Y-%m-%d")
        except Exception:
            continue
    return dt.datetime.utcnow().strftime("%Y-%m-%d")
