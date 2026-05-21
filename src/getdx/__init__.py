from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("getdx")
except PackageNotFoundError:
    __version__ = "unknown"

from getdx.client import DXClient
from getdx.config import DXClientConfig, DXDataCloudConfig, DXWebConfig, RetryConfig
from getdx.data_cloud.client import DXDataCloudClient
from getdx.errors import (
    DXAPIError,
    DXArgumentError,
    DXAuthError,
    DXClientConfigurationError,
    DXClientNotConfiguredError,
    DXFeatureUnavailableError,
    DXPermissionError,
    DXRateLimitError,
    DXResponseError,
    DXServerError,
    DXTransportError,
    DXValidationError,
)
from getdx.web.aggregates import EntityOverview, EntityRelationsGraph
from getdx.web.client import DXWebClient

__all__ = [
    "DXAPIError",
    "DXArgumentError",
    "DXAuthError",
    "DXClient",
    "DXClientConfig",
    "DXClientConfigurationError",
    "DXClientNotConfiguredError",
    "DXDataCloudClient",
    "DXDataCloudConfig",
    "DXFeatureUnavailableError",
    "DXPermissionError",
    "DXRateLimitError",
    "DXResponseError",
    "DXServerError",
    "DXTransportError",
    "DXValidationError",
    "DXWebClient",
    "DXWebConfig",
    "EntityOverview",
    "EntityRelationsGraph",
    "RetryConfig",
    "__version__",
]
