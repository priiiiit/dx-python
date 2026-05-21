# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-12

### Added

#### Core client
- `DXClient` — top-level sync client exposing `web` and `data_cloud` namespaces via a context-manager interface.
- `DXWebConfig` and `DXDataCloudConfig` — frozen dataclass configuration objects for each API.
- `DXClientConfig` — composite config for passing both configs together.
- `DXClientNotConfiguredError` raised when an unconfigured namespace is accessed.

#### DX Web API client (`client.web`)
- `entities` — list, info, scorecards, and tasks operations.
- `entity_relations` — list entity relationships with cursor-based pagination.
- `entity_types` — entity type listing.
- `scorecards` — scorecard listing and detail operations.
- `teams` — team listing and detail operations.
- `users` — user listing and detail operations.
- `user_groups` — user group operations.
- `events` — event ingestion and listing.
- `initiatives` — initiative listing and detail operations.
- `orgfiles` — org file operations.
- `platformx` — PlatformX operations.
- `queries` — query execution operations.
- `snapshots` — snapshot operations.
- `workflow_runs` — workflow run operations.
- `aggregates` — higher-level helpers built on top of core services:
  - `entity_overview(identifier)` — fetches entity info, scorecards, and tasks in a single call and returns an `EntityOverview` dataclass.
  - `entity_relations(identifier, ...)` — fetches all pages of entity relations and returns an `EntityRelationsGraph` dataclass with resolved nodes and edges.

#### DX Data Cloud API client (`client.data_cloud`)
- `custom_data` — upsert and delete custom data records; convenience helpers `delete_by_id` and `delete_by_reference_key`.
- `deployments` — deployment record operations; convenience helpers `set_pull_services_by_github_pull_id` and `set_pull_services_by_repo_and_number`.
- `incidents` — incident record operations.
- `pipeline_runs` — pipeline run record operations.
- `repo_groups` — repository group get and upsert operations.
- `ai_tool_metrics` — AI tool metrics operations.

#### Error hierarchy
- `DXAPIError` — base exception for all SDK errors.
- `DXClientConfigurationError` — raised for invalid or incomplete client configuration.
- `DXClientNotConfiguredError` — raised when accessing a namespace that was not configured.
- `DXArgumentError` — raised for invalid arguments passed to SDK methods.
- `DXResponseError` — raised for HTTP error responses; carries `status_code`, `response_json`, and `response_text`.
- `DXTransportError` — raised for network-level transport failures.
- `DXAuthError` — raised on HTTP 401 responses.
- `DXPermissionError` — raised on HTTP 403 responses.
- `DXFeatureUnavailableError` — raised when a feature is not available for the account.
- `DXValidationError` — raised on HTTP 422 / request validation failures.
- `DXRateLimitError` — raised on HTTP 429; carries `retry_after_seconds` when the server provides a `Retry-After` header.
- `DXServerError` — raised on HTTP 5xx responses.

#### Retry and transport
- `RetryConfig` — frozen dataclass controlling `max_attempts`, exponential `backoff_base_seconds` / `backoff_max_seconds`, and the set of `retry_statuses` (default: 429, 500, 502, 503, 504).
- Automatic exponential back-off for GET requests; honours the `Retry-After` response header for rate-limit delays.
- Retries on `httpx.TransportError` for GET requests.

#### Auto-generated service wrappers
- Web API and Data Cloud API service modules generated from OpenAPI specs via `scripts/generate_from_openapi.py`.
- Regeneration script accepts `--api-name` and `--spec` arguments to target either API.

#### Packaging and typing
- `py.typed` marker included in the wheel (PEP 561 compliant; fully typed package).
- Supports Python 3.10, 3.11, 3.12, and 3.13.
- Runtime dependencies: `httpx>=0.27.0`, `typing-extensions>=4.12.0`.
- Built with `hatchling>=1.25.0`.

#### Environment variable fallbacks
- `DX_WEB_API_TOKEN` — fallback token for the Web API.
- `DX_DATA_CLOUD_TOKEN` — fallback token for the Data Cloud API.
- `DX_DATA_CLOUD_INSTANCE` — fallback instance name for the Data Cloud API base URL.

[Unreleased]: https://github.com/priiiiit/dx-python/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/priiiiit/dx-python/releases/tag/v0.1.0
