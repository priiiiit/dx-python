from __future__ import annotations

import os

import pytest

from getdx import DXClient, DXDataCloudConfig, DXWebConfig


def _extract_first_identifier(payload):  # type: ignore[no-untyped-def]
    if isinstance(payload, dict):
        for key in ("entities", "items", "results", "data"):
            candidate = payload.get(key)
            if isinstance(candidate, list):
                for item in candidate:
                    if isinstance(item, dict):
                        identifier = item.get("identifier")
                        if isinstance(identifier, str) and identifier:
                            return identifier
    if isinstance(payload, list):
        for item in payload:
            if isinstance(item, dict):
                identifier = item.get("identifier")
                if isinstance(identifier, str) and identifier:
                    return identifier
    return None


def test_live_smoke_web_read_and_aggregate() -> None:
    if os.getenv("RUN_LIVE_DX_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_DX_TESTS=1 to run live smoke tests")

    token = os.getenv("DX_WEB_API_TOKEN")
    if not token:
        pytest.skip("DX_WEB_API_TOKEN is required for live web tests")

    with DXClient(web=DXWebConfig(token=token)) as client:
        listed = client.web.entities.list(limit=1)
        assert isinstance(listed, dict | list)

        identifier = _extract_first_identifier(listed)
        if not identifier:
            pytest.skip("No entity identifier available for web aggregate smoke test")

        overview = client.web.aggregates.entity_overview(identifier)
        assert overview.identifier == identifier


def test_live_smoke_data_cloud_get_repo_group() -> None:
    if os.getenv("RUN_LIVE_DX_TESTS") != "1":
        pytest.skip("Set RUN_LIVE_DX_TESTS=1 to run live smoke tests")

    token = os.getenv("DX_DATA_CLOUD_TOKEN")
    instance = os.getenv("DX_DATA_CLOUD_INSTANCE")
    reference_id = os.getenv("DX_DATA_CLOUD_TEST_REFERENCE_ID")

    if not token or not instance or not reference_id:
        pytest.skip(
            "DX_DATA_CLOUD_TOKEN, DX_DATA_CLOUD_INSTANCE, and DX_DATA_CLOUD_TEST_REFERENCE_ID "
            "are required for live data cloud smoke tests"
        )

    with DXClient(data_cloud=DXDataCloudConfig(token=token, instance=instance)) as client:
        payload = client.data_cloud.repo_groups.get(reference_id=reference_id)
        assert payload.get("ok") is True
