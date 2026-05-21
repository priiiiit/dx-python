from __future__ import annotations

from typing import Any

JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | dict[str, "JSONValue"] | list["JSONValue"]
JSONDict = dict[str, JSONValue]
JSONResponse = JSONValue
QueryScalar = str | int | float | bool
BodyScalar = str | int | float | bool
BodyValue = BodyScalar | dict[str, Any] | list[Any]
