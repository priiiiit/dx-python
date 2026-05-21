from __future__ import annotations

from getdx.config import DXWebConfig
from getdx.http.transport import DXTransport
from getdx.web.aggregates import WebAggregates
from getdx.web.services import (
    EntitiesService,
    EntityRelationsService,
    EntityTypesService,
    EventsService,
    InitiativesService,
    OrgfilesService,
    PlatformxService,
    QueriesService,
    ScorecardsService,
    SnapshotsService,
    TeamsService,
    UserGroupsService,
    UsersService,
    WorkflowRunsService,
)


class DXWebClient:
    def __init__(self, config: DXWebConfig) -> None:
        self._config = config
        self._transport = DXTransport(
            config=config.resolved_transport_config(),
            token=config.resolved_token(),
            api_name="web",
        )

        self.entities = EntitiesService(self._transport)
        self.entity_relations = EntityRelationsService(self._transport)
        self.entity_types = EntityTypesService(self._transport)
        self.events = EventsService(self._transport)
        self.initiatives = InitiativesService(self._transport)
        self.orgfiles = OrgfilesService(self._transport)
        self.platformx = PlatformxService(self._transport)
        self.queries = QueriesService(self._transport)
        self.scorecards = ScorecardsService(self._transport)
        self.snapshots = SnapshotsService(self._transport)
        self.teams = TeamsService(self._transport)
        self.user_groups = UserGroupsService(self._transport)
        self.users = UsersService(self._transport)
        self.workflow_runs = WorkflowRunsService(self._transport)

        self.aggregates = WebAggregates(self)

    @property
    def config(self) -> DXWebConfig:
        return self._config

    def close(self) -> None:
        self._transport.close()
