from __future__ import annotations

import pytest

from getdx.config import APITransportConfig, RetryConfig
from getdx.errors import DXAuthError, DXFeatureUnavailableError
from getdx.http.transport import DXTransport


def _make_transport(api_name: str = "web") -> DXTransport:
    config = APITransportConfig(
        base_url="https://api.getdx.com",
        timeout_seconds=30.0,
        user_agent="test-agent",
        retry=RetryConfig(max_attempts=3, backoff_base_seconds=0, backoff_max_seconds=0),
    )
    return DXTransport(config=config, token="token", api_name=api_name)


def test_maps_401_to_auth_error(httpx_mock) -> None:
    transport = _make_transport("web")
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entities.info?identifier=e-1",
        status_code=401,
        json={"ok": False, "error": "unauthorized"},
    )

    with pytest.raises(DXAuthError):
        transport.request("GET", "/entities.info", params={"identifier": "e-1"})

    transport.close()


def test_retries_get_429_then_succeeds(httpx_mock, monkeypatch: pytest.MonkeyPatch) -> None:
    transport = _make_transport("web")
    monkeypatch.setattr("getdx.http.transport.time.sleep", lambda _: None)

    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entities.info?identifier=e-1",
        status_code=429,
        headers={"Retry-After": "0"},
        json={"ok": False, "error": "rate_limited"},
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entities.info?identifier=e-1",
        status_code=200,
        json={"ok": True, "id": "e-1"},
    )

    payload = transport.request("GET", "/entities.info", params={"identifier": "e-1"})
    assert payload == {"ok": True, "id": "e-1"}
    assert len(httpx_mock.get_requests()) == 2

    transport.close()


def test_data_cloud_401_maps_to_feature_unavailable(httpx_mock) -> None:
    config = APITransportConfig(
        base_url="https://acme.getdx.net/api",
        timeout_seconds=30.0,
        user_agent="test-agent",
        retry=RetryConfig(max_attempts=1),
    )
    transport = DXTransport(config=config, token="token", api_name="data_cloud")
    httpx_mock.add_response(
        method="GET",
        url="https://acme.getdx.net/api/repoGroups.get?reference_id=frontend",
        status_code=401,
        json={"ok": False, "error": "unauthorized"},
    )

    with pytest.raises(DXFeatureUnavailableError):
        transport.request("GET", "/repoGroups.get", params={"reference_id": "frontend"})

    transport.close()
