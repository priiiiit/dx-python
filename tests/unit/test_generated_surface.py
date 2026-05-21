from __future__ import annotations

from getdx.data_cloud.operations import OPERATIONS as DATA_CLOUD_OPERATIONS
from getdx.data_cloud.services import SERVICE_CLASS_BY_TAG as DATA_CLOUD_SERVICE_BY_TAG
from getdx.data_cloud.services.deployments import DeploymentsService
from getdx.web.operations import OPERATIONS as WEB_OPERATIONS
from getdx.web.services import SERVICE_CLASS_BY_TAG as WEB_SERVICE_BY_TAG
from getdx.web.services.initiatives import InitiativesService


class RecorderTransport:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def request(self, method: str, path: str, **kwargs):  # type: ignore[no-untyped-def]
        self.calls.append({"method": method, "path": path, **kwargs})
        return {"ok": True}


def test_all_operations_are_emitted() -> None:
    assert len(WEB_OPERATIONS) == 52
    assert len(DATA_CLOUD_OPERATIONS) == 17


def test_all_generated_methods_exist() -> None:
    for operation in WEB_OPERATIONS:
        service_class = WEB_SERVICE_BY_TAG[operation.tag]
        assert hasattr(service_class, operation.method_name)

    for operation in DATA_CLOUD_OPERATIONS:
        service_class = DATA_CLOUD_SERVICE_BY_TAG[operation.tag]
        assert hasattr(service_class, operation.method_name)


def test_generated_web_query_serialization_is_pythonic() -> None:
    transport = RecorderTransport()
    service = InitiativesService(transport=transport)

    service.list(limit=10, published=True)

    request = transport.calls[0]
    assert request["method"] == "GET"
    assert request["path"] == "/initiatives.list"
    assert request["params"]["limit"] == "10"
    assert request["params"]["published"] == "true"


def test_generated_data_cloud_oneof_payload_method() -> None:
    transport = RecorderTransport()
    service = DeploymentsService(transport=transport)

    payload = {"github_pull_id": 123, "services": [{"identifier": "svc-1"}]}
    service.set_pull_services(payload)

    request = transport.calls[0]
    assert request["method"] == "POST"
    assert request["path"] == "/deployments.setPullServices"
    assert request["json_body"] == payload
