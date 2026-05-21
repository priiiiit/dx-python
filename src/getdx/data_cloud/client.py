from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from getdx.config import DXDataCloudConfig
from getdx.data_cloud.services import (
    AiToolMetricsService,
    CustomDataService,
    DeploymentsService,
    IncidentsService,
    PipelineRunsService,
    RepoGroupsService,
)
from getdx.errors import DXArgumentError
from getdx.helpers import JSONReturn
from getdx.http.transport import DXTransport
from getdx.types import BodyValue


class CustomDataAPI:
    def __init__(self, service: CustomDataService) -> None:
        self._service = service

    def get(
        self,
        *,
        id: str | None = None,
        reference: str | None = None,
        key: str | None = None,
    ) -> JSONReturn:
        if id is not None:
            if reference is not None or key is not None:
                raise DXArgumentError(
                    "Pass either id or reference+key for custom_data.get, not both."
                )
            return self._service.get(id=id)

        if reference is not None and key is not None:
            return self._service.get(reference=reference, key=key)

        raise DXArgumentError("custom_data.get requires id or both reference and key.")

    def get_all_by_reference(self, reference: str) -> JSONReturn:
        return self._service.get_all_by_reference(reference=reference)

    def set(
        self,
        *,
        reference: BodyValue,
        key: BodyValue,
        value: BodyValue,
        timestamp: BodyValue | None = None,
    ) -> JSONReturn:
        return self._service.set(reference=reference, key=key, value=value, timestamp=timestamp)

    def set_all(self, *, data: BodyValue) -> JSONReturn:
        return self._service.set_all(data=data)

    def delete(
        self,
        *,
        id: str | None = None,
        reference: str | None = None,
        key: str | None = None,
    ) -> JSONReturn:
        if id is not None:
            if reference is not None or key is not None:
                raise DXArgumentError(
                    "Pass either id or reference+key for custom_data.delete, not both."
                )
            return self._service.delete(payload={"id": id})

        if reference is not None and key is not None:
            return self._service.delete(payload={"reference": reference, "key": key})

        raise DXArgumentError("custom_data.delete requires id or both reference and key.")

    def delete_by_id(self, id: str) -> JSONReturn:
        return self._service.delete(payload={"id": id})

    def delete_by_reference_key(self, reference: str, key: str) -> JSONReturn:
        return self._service.delete(payload={"reference": reference, "key": key})

    def delete_all_by_reference(self, *, reference: BodyValue) -> JSONReturn:
        return self._service.delete_all_by_reference(reference=reference)


class RepoGroupsAPI:
    def __init__(self, service: RepoGroupsService) -> None:
        self._service = service

    def get(self, *, id: str | None = None, reference_id: str | None = None) -> JSONReturn:
        selector = _exactly_one_selector(
            id=id, reference_id=reference_id, method_name="repo_groups.get"
        )
        return self._service.get(**selector)

    def delete(
        self, *, id: BodyValue | None = None, reference_id: BodyValue | None = None
    ) -> JSONReturn:
        selector = _exactly_one_selector(
            id=id,
            reference_id=reference_id,
            method_name="repo_groups.delete",
        )
        return self._service.delete(**selector)

    def upsert(
        self,
        *,
        name: BodyValue,
        id: BodyValue | None = None,
        reference_id: BodyValue | None = None,
        parent_id: BodyValue | None = None,
        repos: BodyValue | None = None,
    ) -> JSONReturn:
        return self._service.upsert(
            name=name,
            id=id,
            reference_id=reference_id,
            parent_id=parent_id,
            repos=repos,
        )

    def add_repos(
        self,
        *,
        repos: BodyValue,
        id: BodyValue | None = None,
        reference_id: BodyValue | None = None,
    ) -> JSONReturn:
        selector = _exactly_one_selector(
            id=id,
            reference_id=reference_id,
            method_name="repo_groups.add_repos",
        )
        return self._service.add_repos(repos=repos, **selector)

    def remove_repos(
        self,
        *,
        repos: BodyValue,
        id: BodyValue | None = None,
        reference_id: BodyValue | None = None,
    ) -> JSONReturn:
        selector = _exactly_one_selector(
            id=id,
            reference_id=reference_id,
            method_name="repo_groups.remove_repos",
        )
        return self._service.remove_repos(repos=repos, **selector)


class DeploymentsAPI:
    def __init__(self, service: DeploymentsService) -> None:
        self._service = service

    def create(
        self,
        *,
        deployed_at: BodyValue,
        service: BodyValue,
        commit_sha: BodyValue | None = None,
        integration_branch: BodyValue | None = None,
        merge_commit_shas: BodyValue | None = None,
        metadata: BodyValue | None = None,
        reference_id: BodyValue | None = None,
        repository: BodyValue | None = None,
        source_name: BodyValue | None = None,
        source_url: BodyValue | None = None,
        success: BodyValue | None = None,
    ) -> JSONReturn:
        return self._service.create(
            deployed_at=deployed_at,
            service=service,
            commit_sha=commit_sha,
            integration_branch=integration_branch,
            merge_commit_shas=merge_commit_shas,
            metadata=metadata,
            reference_id=reference_id,
            repository=repository,
            source_name=source_name,
            source_url=source_url,
            success=success,
        )

    def set_pull_services(self, *, payload: dict[str, Any]) -> JSONReturn:
        return self._service.set_pull_services(payload=payload)

    def set_pull_services_by_github_pull_id(
        self,
        *,
        github_pull_id: int,
        services: Sequence[dict[str, Any]],
    ) -> JSONReturn:
        return self._service.set_pull_services(
            payload={
                "github_pull_id": github_pull_id,
                "services": list(services),
            }
        )

    def set_pull_services_by_repo_and_number(
        self,
        *,
        repository: str,
        pull_number: int,
        services: Sequence[dict[str, Any]],
    ) -> JSONReturn:
        return self._service.set_pull_services(
            payload={
                "repository": repository,
                "pull_number": pull_number,
                "services": list(services),
            }
        )


class PipelineRunsAPI:
    def __init__(self, service: PipelineRunsService) -> None:
        self._service = service

    def upsert(
        self,
        *,
        pipeline_name: BodyValue,
        pipeline_source: BodyValue,
        reference_id: BodyValue,
        started_at: BodyValue,
        commit_sha: BodyValue | None = None,
        email: BodyValue | None = None,
        finished_at: BodyValue | None = None,
        github_username: BodyValue | None = None,
        gitlab_username: BodyValue | None = None,
        head_branch: BodyValue | None = None,
        pr_number: BodyValue | None = None,
        repository: BodyValue | None = None,
        source_url: BodyValue | None = None,
        status: BodyValue | None = None,
    ) -> JSONReturn:
        if (commit_sha is not None or pr_number is not None) and repository is None:
            raise DXArgumentError(
                "pipeline_runs.upsert requires repository when commit_sha/pr_number is set."
            )

        return self._service.upsert(
            pipeline_name=pipeline_name,
            pipeline_source=pipeline_source,
            reference_id=reference_id,
            started_at=started_at,
            commit_sha=commit_sha,
            email=email,
            finished_at=finished_at,
            github_username=github_username,
            gitlab_username=gitlab_username,
            head_branch=head_branch,
            pr_number=pr_number,
            repository=repository,
            source_url=source_url,
            status=status,
        )


class DXDataCloudClient:
    def __init__(self, config: DXDataCloudConfig) -> None:
        self._config = config
        self._transport = DXTransport(
            config=config.resolved_transport_config(),
            token=config.resolved_token(),
            api_name="data_cloud",
        )

        self.ai_tool_metrics = AiToolMetricsService(self._transport)
        self.custom_data = CustomDataAPI(CustomDataService(self._transport))
        self.deployments = DeploymentsAPI(DeploymentsService(self._transport))
        self.incidents = IncidentsService(self._transport)
        self.pipeline_runs = PipelineRunsAPI(PipelineRunsService(self._transport))
        self.repo_groups = RepoGroupsAPI(RepoGroupsService(self._transport))

    @property
    def config(self) -> DXDataCloudConfig:
        return self._config

    def close(self) -> None:
        self._transport.close()


def _exactly_one_selector(
    *,
    id: BodyValue | None,
    reference_id: BodyValue | None,
    method_name: str,
) -> dict[str, BodyValue]:
    if id is not None and reference_id is not None:
        raise DXArgumentError(f"{method_name} accepts either id or reference_id, not both.")
    if id is None and reference_id is None:
        raise DXArgumentError(f"{method_name} requires id or reference_id.")
    if id is not None:
        return {"id": id}
    return {"reference_id": reference_id}
