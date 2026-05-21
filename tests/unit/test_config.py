from __future__ import annotations

import pytest

from getdx.config import DXDataCloudConfig, DXWebConfig


def test_web_resolved_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DX_WEB_API_TOKEN", "web-token")
    config = DXWebConfig(token=None)
    assert config.resolved_token() == "web-token"


def test_web_resolved_token_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DX_WEB_API_TOKEN", raising=False)
    config = DXWebConfig(token=None)
    with pytest.raises(ValueError):
        config.resolved_token()


def test_data_cloud_base_url_from_instance(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DX_DATA_CLOUD_INSTANCE", "myinstance")
    config = DXDataCloudConfig(token="token")
    assert config.resolved_base_url() == "https://myinstance.getdx.net/api"


def test_data_cloud_base_url_override() -> None:
    config = DXDataCloudConfig(token="token", base_url="https://custom.getdx.net/api/")
    assert config.resolved_base_url() == "https://custom.getdx.net/api"
