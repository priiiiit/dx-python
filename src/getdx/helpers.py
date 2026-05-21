from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from getdx.types import QueryScalar

JSONReturn = dict[str, Any] | list[Any]


def _coerce_query_value(value: QueryScalar | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _clean_mapping(values: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}
