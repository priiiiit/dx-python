"""
Using environment variables for credentials and both APIs in one client.

Set these before running:
  export DX_WEB_API_TOKEN=your-web-token
  export DX_DATA_CLOUD_TOKEN=your-data-cloud-token
  export DX_DATA_CLOUD_INSTANCE=yourinstance
"""

from getdx import DXClient, DXDataCloudConfig, DXWebConfig

# Tokens/instance are picked up from environment variables automatically
with DXClient(
    web=DXWebConfig(),
    data_cloud=DXDataCloudConfig(),
) as client:
    # Web API
    entity = client.web.entities.info("checkout-service")
    print("Entity:", entity)

    # Data Cloud API
    group = client.data_cloud.repo_groups.get(reference_id="backend-team")
    print("Repo group:", group)
