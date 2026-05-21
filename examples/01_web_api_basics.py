"""
Web API basics: listing entities, teams, scorecards, and initiatives.
"""

from getdx import DXClient, DXWebConfig

with DXClient(web=DXWebConfig(token="<DX_WEB_API_TOKEN>")) as client:
    # List all entities (first page)
    entities = client.web.entities.list(limit=20)
    print("Entities:", entities)

    # Get details for a specific entity
    entity = client.web.entities.info("my-service")
    print("Entity:", entity)

    # List all teams
    teams = client.web.teams.list(limit=10)
    print("Teams:", teams)

    # Look up a team by reference ID
    team = client.web.teams.info(reference_id="platform-team")
    print("Team:", team)

    # List all scorecards
    scorecards = client.web.scorecards.list()
    print("Scorecards:", scorecards)

    # List published initiatives
    initiatives = client.web.initiatives.list(published=True)
    print("Initiatives:", initiatives)
