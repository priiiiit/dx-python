from __future__ import annotations

import time
from collections.abc import Mapping
from typing import Any, cast

import httpx

from getdx.config import APITransportConfig
from getdx.errors import (
    DXAuthError,
    DXFeatureUnavailableError,
    DXPermissionError,
    DXRateLimitError,
    DXResponseError,
    DXServerError,
    DXTransportError,
    DXValidationError,
)
from getdx.http.retry import (
    compute_retry_delay,
    parse_retry_after_seconds,
    should_retry_exception,
    should_retry_status,
)
from getdx.types import JSONResponse


class DXTransport:
    def __init__(self, config: APITransportConfig, token: str, *, api_name: str) -> None:
        self._config = config
        self._api_name = api_name
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": config.user_agent,
        }
        self._client = httpx.Client(
            base_url=config.base_url.rstrip("/"),
            headers=headers,
            timeout=config.timeout_seconds,
        )

    def close(self) -> None:
        self._client.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        json_body: Mapping[str, Any] | None = None,
    ) -> JSONResponse:
        upper_method = method.upper()
        max_attempts = self._config.retry.max_attempts if upper_method == "GET" else 1

        for attempt in range(1, max_attempts + 1):
            try:
                response = self._client.request(upper_method, path, params=params, json=json_body)
            except Exception as exc:
                if attempt < max_attempts and should_retry_exception(upper_method, exc):
                    delay = compute_retry_delay(attempt, self._config.retry)
                    time.sleep(delay)
                    continue
                raise DXTransportError(f"DX request failed before response: {exc}") from exc

            if 200 <= response.status_code < 300:
                return self._parse_json(response)

            if attempt < max_attempts and should_retry_status(
                upper_method,
                response.status_code,
                self._config.retry.retry_statuses,
            ):
                delay = compute_retry_delay(
                    attempt,
                    self._config.retry,
                    response.headers.get("Retry-After"),
                )
                time.sleep(delay)
                continue

            raise self._build_http_error(response)

        raise DXTransportError("Retry loop exhausted without response")

    def _parse_json(self, response: httpx.Response) -> JSONResponse:
        try:
            return cast(JSONResponse, response.json())
        except ValueError as exc:
            raise DXResponseError(
                "DX API returned non-JSON response",
                status_code=response.status_code,
                response_text=response.text,
            ) from exc

    def _build_http_error(self, response: httpx.Response) -> DXResponseError:
        payload: Any | None
        message = f"DX API request failed with status {response.status_code}"
        try:
            payload = response.json()
            if isinstance(payload, dict):
                error_message = payload.get("error") or payload.get("message")
                if isinstance(error_message, str) and error_message:
                    message = f"DX API error: {error_message}"
        except ValueError:
            payload = None

        kwargs: dict[str, Any] = {
            "status_code": response.status_code,
            "response_json": payload,
            "response_text": response.text,
        }

        if self._api_name == "data_cloud" and response.status_code in (401, 403):
            return DXFeatureUnavailableError(
                "DX Data Cloud request was rejected. Verify token and workspace entitlement.",
                **kwargs,
            )
        if response.status_code == 401:
            return DXAuthError(message, **kwargs)
        if response.status_code == 403:
            return DXPermissionError(message, **kwargs)
        if response.status_code == 422:
            return DXValidationError(message, **kwargs)
        if response.status_code == 429:
            return DXRateLimitError(
                message,
                retry_after_seconds=parse_retry_after_seconds(response.headers.get("Retry-After")),
                **kwargs,
            )
        if response.status_code >= 500:
            return DXServerError(message, **kwargs)
        return DXResponseError(message, **kwargs)
