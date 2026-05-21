from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from getdx.helpers import JSONReturn

if TYPE_CHECKING:
    from getdx.web.client import DXWebClient


@dataclass(frozen=True)
class EntityOverview:
    identifier: str
    entity: JSONReturn
    scorecards: JSONReturn
    tasks: JSONReturn
    raw: dict[str, JSONReturn]


@dataclass(frozen=True)
class EntityRelationsGraph:
    identifier: str
    entity: JSONReturn
    relations: list[dict[str, Any]]
    nodes: dict[str, dict[str, Any]]
    edges: list[dict[str, Any]]
    pages: list[JSONReturn]


class WebAggregates:
    def __init__(self, client: DXWebClient) -> None:
        self._client = client

    def entity_overview(self, identifier: str) -> EntityOverview:
        entity = self._client.entities.info(identifier)
        scorecards = self._client.entities.scorecards(identifier)
        tasks = self._client.entities.tasks(identifier)
        return EntityOverview(
            identifier=identifier,
            entity=entity,
            scorecards=scorecards,
            tasks=tasks,
            raw={
                "entity": entity,
                "scorecards": scorecards,
                "tasks": tasks,
            },
        )

    def entity_relations(
        self,
        identifier: str,
        relation_type: str | None = None,
        limit: int = 100,
        *,
        max_pages: int = 100,
    ) -> EntityRelationsGraph:
        entity = self._client.entities.info(identifier)

        pages: list[JSONReturn] = []
        relations: list[dict[str, Any]] = []
        seen_cursors: set[str] = set()
        cursor: str | None = None

        for _ in range(max_pages):
            page = self._client.entity_relations.list(
                entity_identifier=identifier,
                relation_type=relation_type,
                cursor=cursor,
                limit=limit,
            )
            pages.append(page)
            relations.extend(_extract_relations(page))

            next_cursor = _extract_next_cursor(page)
            if not next_cursor or next_cursor in seen_cursors:
                break
            seen_cursors.add(next_cursor)
            cursor = next_cursor

        nodes: dict[str, dict[str, Any]] = {identifier: {"identifier": identifier}}
        edges: list[dict[str, Any]] = []

        for relation in relations:
            source = _pick_identifier(
                relation,
                "source",
                "source_identifier",
                "from",
                "entity_identifier",
            )
            target = _pick_identifier(
                relation,
                "target",
                "target_identifier",
                "to",
                "related_entity_identifier",
            )
            if source:
                nodes.setdefault(source, {"identifier": source})
            if target:
                nodes.setdefault(target, {"identifier": target})
            if source and target:
                edges.append({"source": source, "target": target, "relation": relation})

        return EntityRelationsGraph(
            identifier=identifier,
            entity=entity,
            relations=relations,
            nodes=nodes,
            edges=edges,
            pages=pages,
        )


def _extract_relations(payload: JSONReturn) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []

    candidates = [
        payload.get("relations"),
        payload.get("items"),
        payload.get("results"),
        payload.get("data"),
    ]
    for candidate in candidates:
        if isinstance(candidate, list):
            return [item for item in candidate if isinstance(item, dict)]
        if isinstance(candidate, dict):
            for key in ("relations", "items", "results", "data"):
                nested = candidate.get(key)
                if isinstance(nested, list):
                    return [item for item in nested if isinstance(item, dict)]
    return []


def _extract_next_cursor(payload: JSONReturn) -> str | None:
    if not isinstance(payload, dict):
        return None
    for key in ("next_cursor", "nextCursor", "cursor", "next"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    pagination = payload.get("pagination")
    if isinstance(pagination, dict):
        for key in ("next_cursor", "nextCursor", "cursor", "next"):
            value = pagination.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _pick_identifier(relation: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = relation.get(key)
        if isinstance(value, str) and value:
            return value
        if isinstance(value, dict):
            nested_value = value.get("identifier")
            if isinstance(nested_value, str) and nested_value:
                return nested_value
    return None
