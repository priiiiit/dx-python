from __future__ import annotations

from getdx import DXClient, DXWebConfig


def _make_client() -> DXClient:
    return DXClient(web=DXWebConfig(token="web-token"))


def test_entity_overview_aggregate(httpx_mock) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/catalog.entities.info?identifier=e-1",
        status_code=200,
        json={"ok": True, "entity": {"identifier": "e-1"}},
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/catalog.entities.scorecards?identifier=e-1",
        status_code=200,
        json={"ok": True, "scorecards": []},
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/catalog.entities.tasks?identifier=e-1",
        status_code=200,
        json={"ok": True, "tasks": []},
    )

    with _make_client() as client:
        overview = client.web.aggregates.entity_overview("e-1")

    assert overview.identifier == "e-1"
    assert overview.raw["entity"]["ok"] is True
    assert overview.raw["scorecards"]["ok"] is True
    assert overview.raw["tasks"]["ok"] is True


def test_entity_relations_aggregate_paginates(httpx_mock) -> None:
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/catalog.entities.info?identifier=e-1",
        status_code=200,
        json={"ok": True, "entity": {"identifier": "e-1"}},
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entityRelations.list?entity_identifier=e-1&limit=2",
        status_code=200,
        json={
            "ok": True,
            "relations": [{"source": "e-1", "target": "e-2", "type": "depends_on"}],
            "next_cursor": "next-1",
        },
    )
    httpx_mock.add_response(
        method="GET",
        url="https://api.getdx.com/entityRelations.list?entity_identifier=e-1&cursor=next-1&limit=2",
        status_code=200,
        json={
            "ok": True,
            "relations": [{"source": "e-2", "target": "e-3", "type": "uses"}],
        },
    )

    with _make_client() as client:
        graph = client.web.aggregates.entity_relations("e-1", limit=2)

    assert graph.identifier == "e-1"
    assert len(graph.relations) == 2
    assert len(graph.edges) == 2
    assert "e-1" in graph.nodes
    assert "e-2" in graph.nodes
    assert "e-3" in graph.nodes
    assert len(graph.pages) == 2
