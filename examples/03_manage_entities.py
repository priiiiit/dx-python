"""
Create, update, and upsert entities.
"""

from getdx import DXClient, DXWebConfig

with DXClient(web=DXWebConfig(token="<DX_WEB_API_TOKEN>")) as client:
    # Create a new entity
    result = client.web.entities.create(
        entity_type_identifier="service",
        identifier="payments-service",
        name="Payments Service",
        description="Handles all payment processing",
        properties={"tier": "1", "language": "python"},
    )
    print("Created:", result)

    # Update an existing entity
    result = client.web.entities.update(
        identifier="payments-service",
        description="Handles all payment processing (updated)",
    )
    print("Updated:", result)

    # Upsert — create or update in one call
    result = client.web.entities.upsert(
        entity_type_identifier="service",
        identifier="notifications-service",
        name="Notifications Service",
        properties={"tier": "2"},
    )
    print("Upserted:", result)
