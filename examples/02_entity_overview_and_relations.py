"""
Entity overview and relations graph using the aggregate helpers.
"""

from getdx import DXClient, DXWebConfig

with DXClient(web=DXWebConfig(token="<DX_WEB_API_TOKEN>")) as client:
    # Fetch entity info + scorecards + tasks in one call
    overview = client.web.aggregates.entity_overview("checkout-service")
    print("Entity:", overview.entity)
    print("Open tasks:", overview.tasks)
    print("Scorecards:", overview.scorecards)

    # Build a full relations graph (auto-paginates)
    graph = client.web.aggregates.entity_relations("checkout-service")
    print(f"Nodes ({len(graph.nodes)}):", list(graph.nodes.keys()))
    print(f"Edges ({len(graph.edges)}):")
    for edge in graph.edges:
        print(f"  {edge['source']} -> {edge['target']}")
