"""
Data Cloud API: recording deployments.
"""

from getdx import DXClient, DXDataCloudConfig

with DXClient(
    data_cloud=DXDataCloudConfig(
        token="<DX_DATA_CLOUD_TOKEN>",
        instance="yourinstance",
    )
) as client:
    # Record a deployment
    result = client.data_cloud.deployments.create(
        service="payments-service",
        deployed_at="2026-03-12T10:00:00Z",
        commit_sha="abc123def456",
        repository="org/payments-service",
        success=True,
    )
    print("Deployment recorded:", result)

    # Associate a pull request with services (by GitHub pull ID)
    result = client.data_cloud.deployments.set_pull_services_by_github_pull_id(
        github_pull_id=12345,
        services=[{"name": "payments-service"}, {"name": "billing-service"}],
    )
    print("Pull services set:", result)

    # Associate a pull request with services (by repo + PR number)
    result = client.data_cloud.deployments.set_pull_services_by_repo_and_number(
        repository="org/payments-service",
        pull_number=42,
        services=[{"name": "payments-service"}],
    )
    print("Pull services set:", result)
