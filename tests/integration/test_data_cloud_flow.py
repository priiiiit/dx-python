from __future__ import annotations

import pytest

from getdx import DXArgumentError, DXClient, DXDataCloudConfig


def _make_client() -> DXClient:
    return DXClient(data_cloud=DXDataCloudConfig(token="dc-token", instance="acme"))


def test_repo_groups_selector_validation() -> None:
    with _make_client() as client:
        with pytest.raises(DXArgumentError):
            client.data_cloud.repo_groups.get()
        with pytest.raises(DXArgumentError):
            client.data_cloud.repo_groups.get(id="1", reference_id="ref")


def test_custom_data_delete_oneof_variants(httpx_mock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="https://acme.getdx.net/api/customData.delete",
        status_code=200,
        json={"ok": True},
    )
    httpx_mock.add_response(
        method="POST",
        url="https://acme.getdx.net/api/customData.delete",
        status_code=200,
        json={"ok": True},
    )

    with _make_client() as client:
        client.data_cloud.custom_data.delete_by_id("abc")
        client.data_cloud.custom_data.delete_by_reference_key("org/repo", "k")

    requests = httpx_mock.get_requests()
    assert requests[0].read().decode("utf-8") == '{"id":"abc"}'
    assert requests[1].read().decode("utf-8") == '{"reference":"org/repo","key":"k"}'


def test_deployments_set_pull_services_helpers(httpx_mock) -> None:
    httpx_mock.add_response(
        method="POST",
        url="https://acme.getdx.net/api/deployments.setPullServices",
        status_code=200,
        json={"ok": True},
    )

    with _make_client() as client:
        payload = client.data_cloud.deployments.set_pull_services_by_github_pull_id(
            github_pull_id=123,
            services=[{"identifier": "svc-1"}],
        )

    assert payload["ok"] is True


def test_pipeline_runs_requires_repository_when_commit_or_pr() -> None:
    with _make_client() as client, pytest.raises(DXArgumentError):
        client.data_cloud.pipeline_runs.upsert(
            pipeline_name="build",
            pipeline_source="github-actions",
            reference_id="run-1",
            started_at="2025-01-01T00:00:00Z",
            commit_sha="abc123",
        )
