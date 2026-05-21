from __future__ import annotations

import pytest

from getdx import DXClient, DXClientNotConfiguredError, DXDataCloudConfig, DXWebConfig


def test_web_requests_are_fresh(httpx_mock) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entities.info?identifier=e-1",
        status_code=200,
        json={"ok": True, "version": 1},
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entities.info?identifier=e-1",
        status_code=200,
        json={"ok": True, "version": 2},
    )

    with DXClient(web=DXWebConfig(token="web-token")) as client:
        first = client.web.entities.info("e-1")
        second = client.web.entities.info("e-1")

    assert first["version"] == 1
    assert second["version"] == 2


def test_unconfigured_namespace_raises() -> None:
    with (
        DXClient(web=DXWebConfig(token="web-token")) as client,
        pytest.raises(DXClientNotConfiguredError),
    ):
        _ = client.data_cloud


def test_dual_namespace_client(httpx_mock) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entities.info?identifier=e-1",
        status_code=200,
        json={"ok": True, "entity": {"identifier": "e-1"}},
    )
    httpx_mock.add_response(
        method="GET",
        url="https://acme.getdx.net/api/repoGroups.get?reference_id=frontend",
        status_code=200,
        json={"ok": True, "data": {"reference_id": "frontend"}},
    )

    with DXClient(
        web=DXWebConfig(token="web-token"),
        data_cloud=DXDataCloudConfig(token="dc-token", instance="acme"),
    ) as client:
        web_payload = client.web.entities.info("e-1")
        data_payload = client.data_cloud.repo_groups.get(reference_id="frontend")

    assert web_payload["ok"] is True
    assert data_payload["ok"] is True
