# Contributing to getdx

Thank you for your interest in contributing! This guide covers everything you need to get started.

## Development Setup

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Clone the repository
git clone https://github.com/priiiiit/dx-python.git
cd dx-python

# Install all dependencies including dev extras
uv sync --dev
```

**Requirements:** Python 3.10+

## Project Structure

```
src/getdx/        # Package source code
tests/            # Test suite
scripts/          # Code generation and other utilities
specs/            # OpenAPI specifications
```

## Running Tests

```bash
uv run pytest
```

Tests use [pytest-httpx](https://github.com/Colin-b/pytest-httpx) to mock HTTP interactions. Please add tests for any new functionality or bug fixes.

Optional live smoke tests (require real API credentials):

```bash
RUN_LIVE_DX_TESTS=1 uv run pytest tests/live -q
```

## Code Style

This project uses [ruff](https://docs.astral.sh/ruff/) for formatting and linting (line length: 100).

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Auto-fix lint issues where possible
uv run ruff check --fix .
```

Please ensure your code passes both format and lint checks before opening a pull request.

## Auto-Generated API Services

The service wrappers for the DX Web API and DX Data Cloud API are **auto-generated** from OpenAPI specifications via `scripts/generate_from_openapi.py`. Do not hand-edit these files — any manual changes will be overwritten the next time code generation runs.

To regenerate the API wrappers after updating a spec:

```bash
# Regenerate from the DX Web API spec
uv run python scripts/generate_from_openapi.py --api-name web --spec specs/dx_web_api_openapi.json

# Regenerate from the DX Data Cloud API spec
uv run python scripts/generate_from_openapi.py --api-name data_cloud --spec specs/dx_data_cloud_api_openapi.json
```

If you need to change the structure or behavior of the generated code, modify the generator script rather than the generated output.

## Building the Package

```bash
uv build
```

## Pull Request Process

1. Fork the repository and create a branch from `main`.
2. Make your changes, following the code style guidelines above.
3. Add or update tests as appropriate.
4. Ensure all checks pass:
   ```bash
   uv run ruff format .
   uv run ruff check .
   uv run pytest
   ```
5. Open a pull request against `main` with a clear description of what changed and why.

For significant changes, consider opening an issue first to discuss the approach before investing time in implementation.
