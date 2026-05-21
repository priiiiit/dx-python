"""
Data Cloud API: managing repo groups.
"""

from getdx import DXClient, DXDataCloudConfig

with DXClient(
    data_cloud=DXDataCloudConfig(
        token="<DX_DATA_CLOUD_TOKEN>",
        instance="yourinstance",
    )
) as client:
    # Create or update a repo group
    result = client.data_cloud.repo_groups.upsert(
        name="Frontend Team",
        reference_id="frontend-team",
        repos=["org/web-app", "org/design-system"],
    )
    print("Upserted:", result)

    # Retrieve by reference ID
    group = client.data_cloud.repo_groups.get(reference_id="frontend-team")
    print("Group:", group)

    # Add repos to an existing group
    result = client.data_cloud.repo_groups.add_repos(
        reference_id="frontend-team",
        repos=["org/mobile-app"],
    )
    print("Added repos:", result)

    # Remove repos from a group
    result = client.data_cloud.repo_groups.remove_repos(
        reference_id="frontend-team",
        repos=["org/mobile-app"],
    )
    print("Removed repos:", result)

    # Delete the group
    client.data_cloud.repo_groups.delete(reference_id="frontend-team")
    print("Deleted")
