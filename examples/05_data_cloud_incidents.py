"""
Data Cloud API: upserting incidents.
"""

from getdx import DXClient, DXDataCloudConfig

with DXClient(
    data_cloud=DXDataCloudConfig(
        token="<DX_DATA_CLOUD_TOKEN>",
        instance="yourinstance",
    )
) as client:
    # Open a new incident
    result = client.data_cloud.incidents.upsert(
        reference_id="INC-001",
        name="Database latency spike",
        started_at="2026-03-12T08:00:00Z",
        services=["payments-service", "checkout-service"],
        priority="p1",
        source_url="https://incidents.example.com/INC-001",
    )
    print("Incident opened:", result)

    # Resolve the incident
    result = client.data_cloud.incidents.upsert(
        reference_id="INC-001",
        name="Database latency spike",
        started_at="2026-03-12T08:00:00Z",
        resolved_at="2026-03-12T09:30:00Z",
        services=["payments-service", "checkout-service"],
        priority="p1",
    )
    print("Incident resolved:", result)
