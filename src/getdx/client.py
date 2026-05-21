from __future__ import annotations

from getdx.config import DXClientConfig, DXDataCloudConfig, DXWebConfig
from getdx.data_cloud.client import DXDataCloudClient
from getdx.errors import DXClientConfigurationError, DXClientNotConfiguredError
from getdx.web.client import DXWebClient


class DXClient:
    def __init__(
        self,
        *,
        web: DXWebConfig | None = None,
        data_cloud: DXDataCloudConfig | None = None,
        config: DXClientConfig | None = None,
    ) -> None:
        resolved_web = web if web is not None else (config.web if config is not None else None)
        resolved_data_cloud = (
            data_cloud
            if data_cloud is not None
            else (config.data_cloud if config is not None else None)
        )

        if resolved_web is None and resolved_data_cloud is None:
            raise DXClientConfigurationError(
                "DXClient requires at least one API config. Provide web=DXWebConfig(...) "
                "and/or data_cloud=DXDataCloudConfig(...)."
            )

        self._web = DXWebClient(resolved_web) if resolved_web is not None else None
        self._data_cloud = (
            DXDataCloudClient(resolved_data_cloud) if resolved_data_cloud is not None else None
        )

    @property
    def has_web(self) -> bool:
        return self._web is not None

    @property
    def has_data_cloud(self) -> bool:
        return self._data_cloud is not None

    @property
    def web(self) -> DXWebClient:
        if self._web is None:
            raise DXClientNotConfiguredError(
                "DXClient.web is not configured. "
                "Pass web=DXWebConfig(...) when constructing DXClient."
            )
        return self._web

    @property
    def data_cloud(self) -> DXDataCloudClient:
        if self._data_cloud is None:
            raise DXClientNotConfiguredError(
                "DXClient.data_cloud is not configured. Pass data_cloud=DXDataCloudConfig(...) "
                "when constructing DXClient."
            )
        return self._data_cloud

    def close(self) -> None:
        if self._web is not None:
            self._web.close()
        if self._data_cloud is not None:
            self._data_cloud.close()

    def __enter__(self) -> DXClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[no-untyped-def]
        self.close()
