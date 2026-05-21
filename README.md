# getdx

[![PyPI version](https://img.shields.io/pypi/v/getdx.svg)](https://pypi.org/project/getdx/)
[![Python versions](https://img.shields.io/pypi/pyversions/getdx.svg)](https://pypi.org/project/getdx/)
[![CI](https://github.com/priiiiit/dx-python/actions/workflows/ci.yml/badge.svg)](https://github.com/priiiiit/dx-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sync-first Python SDK covering both DX APIs:
- DX Web API (`https://api.getdx.com`)
- DX Data Cloud API (`https://{instance}.getdx.net/api`)

This SDK does not cache API responses. Each call fetches fresh data.

## Install

```bash
pip install getdx
```

Requires Python 3.10+.

## Quickstart

### Web API only
```python
from getdx import DXClient, DXWebConfig

with DXClient(web=DXWebConfig(token="<DX_WEB_API_TOKEN>")) as client:
    entities = client.web.entities.list(limit=10)
    overview = client.web.aggregates.entity_overview("my-entity-id")
    print(entities)
    print(overview.tasks)
```

### Data Cloud API only
```python
from getdx import DXClient, DXDataCloudConfig

with DXClient(
    data_cloud=DXDataCloudConfig(
        token="<DX_DATA_CLOUD_TOKEN>",
        instance="yourinstance",
    )
) as client:
    group = client.data_cloud.repo_groups.get(reference_id="frontend-team")
    print(group)
```

### Both APIs in one client
```python
from getdx import DXClient, DXDataCloudConfig, DXWebConfig

with DXClient(
    web=DXWebConfig(token="<DX_WEB_API_TOKEN>"),
    data_cloud=DXDataCloudConfig(token="<DX_DATA_CLOUD_TOKEN>", instance="yourinstance"),
) as client:
    web_entity = client.web.entities.info("entity-1")
    repo_group = client.data_cloud.repo_groups.get(reference_id="frontend-team")
```

## Data Cloud convenience helpers
- `client.data_cloud.custom_data.delete_by_id(id)`
- `client.data_cloud.custom_data.delete_by_reference_key(reference, key)`
- `client.data_cloud.deployments.set_pull_services_by_github_pull_id(...)`
- `client.data_cloud.deployments.set_pull_services_by_repo_and_number(...)`

## Optional namespace behavior
If `web` or `data_cloud` was not configured on `DXClient`, accessing that namespace raises
`DXClientNotConfiguredError`.

## Environment variables
- `DX_WEB_API_TOKEN` for Web API token fallback
- `DX_DATA_CLOUD_TOKEN` for Data Cloud token fallback
- `DX_DATA_CLOUD_INSTANCE` for Data Cloud instance fallback

## Development

Clone and install with `uv`:

```bash
git clone https://github.com/priiiiit/dx-python.git
cd dx-python
uv sync --dev
```

### Regenerate API wrappers
Generated modules live under:
- `src/getdx/web/` (operations.py, services/)
- `src/getdx/data_cloud/` (operations.py, services/)

```bash
uv run python scripts/generate_from_openapi.py \
  --api-name web \
  --spec specs/dx_web_api_openapi.json

uv run python scripts/generate_from_openapi.py \
  --api-name data_cloud \
  --spec specs/dx_data_cloud_api_openapi.json
```

### Testing and linting
```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

Optional live smoke tests:
```bash
RUN_LIVE_DX_TESTS=1 uv run pytest tests/live -q
```

For Data Cloud live smoke, set:
- `DX_DATA_CLOUD_TOKEN`
- `DX_DATA_CLOUD_INSTANCE`
- `DX_DATA_CLOUD_TEST_REFERENCE_ID`

## License

MIT — see [LICENSE](LICENSE).
