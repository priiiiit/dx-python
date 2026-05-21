from __future__ import annotations

import math
import time
from email.utils import parsedate_to_datetime

import httpx

from getdx.config import RetryConfig


def should_retry_status(method: str, status_code: int, retry_statuses: tuple[int, ...]) -> bool:
    return method.upper() == "GET" and status_code in retry_statuses


def should_retry_exception(method: str, exc: Exception) -> bool:
    if method.upper() != "GET":
        return False
    return isinstance(exc, httpx.TransportError)


def parse_retry_after_seconds(retry_after: str | None) -> float | None:
    if not retry_after:
        return None
    value = retry_after.strip()
    if not value:
        return None
    if value.isdigit():
        return float(value)
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return None
    if parsed is None:
        return None
    seconds = parsed.timestamp() - time.time()
    return max(0.0, seconds)


def compute_retry_delay(
    attempt_number: int,
    retry_config: RetryConfig,
    retry_after_header: str | None = None,
) -> float:
    retry_after = parse_retry_after_seconds(retry_after_header)
    if retry_after is not None:
        return min(retry_after, retry_config.backoff_max_seconds)
    exp_backoff = retry_config.backoff_base_seconds * math.pow(2, max(attempt_number - 1, 0))
    return min(exp_backoff, retry_config.backoff_max_seconds)
