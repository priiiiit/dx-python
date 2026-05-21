from __future__ import annotations

from typing import Any


class DXAPIError(Exception):
    """Base exception for DX SDK errors."""


class DXClientConfigurationError(DXAPIError):
    pass


class DXClientNotConfiguredError(DXAPIError):
    pass


class DXArgumentError(DXAPIError):
    pass


class DXResponseError(DXAPIError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_json: Any | None = None,
        response_text: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_json = response_json
        self.response_text = response_text


class DXTransportError(DXAPIError):
    pass


class DXAuthError(DXResponseError):
    pass


class DXPermissionError(DXResponseError):
    pass


class DXFeatureUnavailableError(DXResponseError):
    pass


class DXValidationError(DXResponseError):
    pass


class DXRateLimitError(DXResponseError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_json: Any | None = None,
        response_text: str | None = None,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            response_json=response_json,
            response_text=response_text,
        )
        self.retry_after_seconds = retry_after_seconds


class DXServerError(DXResponseError):
    pass
