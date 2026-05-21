"""
Data Cloud API: setting and retrieving custom data.
"""

from getdx import DXClient, DXDataCloudConfig

with DXClient(
    data_cloud=DXDataCloudConfig(
        token="<DX_DATA_CLOUD_TOKEN>",
        instance="yourinstance",
    )
) as client:
    # Set a single custom data point
    result = client.data_cloud.custom_data.set(
        reference="payments-service",
        key="code_coverage",
        value=87.4,
    )
    print("Set:", result)

    # Set multiple custom data points in one call
    result = client.data_cloud.custom_data.set_all(
        data=[
            {"reference": "payments-service", "key": "code_coverage", "value": 87.4},
            {"reference": "checkout-service", "key": "code_coverage", "value": 91.2},
        ]
    )
    print("Set all:", result)

    # Retrieve by reference + key
    record = client.data_cloud.custom_data.get(
        reference="payments-service",
        key="code_coverage",
    )
    print("Got:", record)

    # Retrieve all data for a reference
    all_records = client.data_cloud.custom_data.get_all_by_reference("payments-service")
    print("All records:", all_records)

    # Delete by ID
    client.data_cloud.custom_data.delete_by_id("some-record-id")

    # Delete by reference + key
    client.data_cloud.custom_data.delete_by_reference_key("payments-service", "code_coverage")
