from __future__ import annotations

import os
from dataclasses import dataclass, field

DEFAULT_WEB_BASE_URL = "https://api.getdx.com"
DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_DATA_CLOUD_URL_TEMPLATE = "https://{instance}.getdx.net/api"


@dataclass(frozen=True)
class RetryConfig:
    max_attempts: int = 3
    backoff_base_seconds: float = 0.25
    backoff_max_seconds: float = 2.0
    retry_statuses: tuple[int, ...] = (429, 500, 502, 503, 504)


@dataclass(frozen=True)
class APITransportConfig:
    base_url: str
    timeout_seconds: float
    user_agent: str
    retry: RetryConfig


@dataclass(frozen=True)
class DXWebConfig:
    token: str | None = None
    base_url: str = DEFAULT_WEB_BASE_URL
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    user_agent: str = "getdx/web"
    retry: RetryConfig = field(default_factory=RetryConfig)

    def resolved_token(self) -> str:
        token = self.token or os.getenv("DX_WEB_API_TOKEN")
        if not token:
            raise ValueError(
                "DX Web API token missing. Set DX_WEB_API_TOKEN or pass token in DXWebConfig."
            )
        return token

    def resolved_transport_config(self) -> APITransportConfig:
        return APITransportConfig(
            base_url=self.base_url.rstrip("/"),
            timeout_seconds=self.timeout_seconds,
            user_agent=self.user_agent,
            retry=self.retry,
        )


@dataclass(frozen=True)
class DXDataCloudConfig:
    token: str | None = None
    instance: str | None = None
    base_url: str | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    user_agent: str = "getdx/data-cloud"
    retry: RetryConfig = field(default_factory=RetryConfig)

    def resolved_token(self) -> str:
        token = self.token or os.getenv("DX_DATA_CLOUD_TOKEN")
        if not token:
            raise ValueError(
                "DX Data Cloud token missing. "
                "Set DX_DATA_CLOUD_TOKEN or pass token in DXDataCloudConfig."
            )
        return token

    def resolved_base_url(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")

        instance = self.instance or os.getenv("DX_DATA_CLOUD_INSTANCE")
        if not instance:
            raise ValueError(
                "DX Data Cloud base URL cannot be resolved. "
                "Set DX_DATA_CLOUD_INSTANCE or pass instance/base_url in DXDataCloudConfig."
            )

        return DEFAULT_DATA_CLOUD_URL_TEMPLATE.format(instance=instance).rstrip("/")

    def resolved_transport_config(self) -> APITransportConfig:
        return APITransportConfig(
            base_url=self.resolved_base_url(),
            timeout_seconds=self.timeout_seconds,
            user_agent=self.user_agent,
            retry=self.retry,
        )


@dataclass(frozen=True)
class DXClientConfig:
    web: DXWebConfig | None = None
    data_cloud: DXDataCloudConfig | None = None
