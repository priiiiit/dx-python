from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SPEC = ROOT / "specs" / "dx_web_api_openapi.json"
DEFAULT_OUTPUT_ROOT = ROOT / "src" / "getdx"


@dataclass(frozen=True)
class ParamSpec:
    name: str
    required: bool
    in_: str
    schema_type: str


@dataclass(frozen=True)
class OperationSpec:
    operation_id: str
    method: str
    path: str
    tag: str
    service_module: str
    service_class: str
    service_attr: str
    method_name: str
    parameters: tuple[ParamSpec, ...]
    body_fields: tuple[ParamSpec, ...]
    has_complex_body: bool
    summary: str


def to_snake(name: str) -> str:
    with_underscores = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    with_underscores = with_underscores.replace(".", "_").replace("-", "_")
    with_underscores = re.sub(r"__+", "_", with_underscores)
    return with_underscores.lower().strip("_")


def to_pascal(name: str) -> str:
    return "".join(part.capitalize() for part in to_snake(name).split("_"))


def load_operations(spec: dict[str, Any]) -> list[OperationSpec]:
    all_operations: list[OperationSpec] = []
    method_names_by_tag: dict[str, set[str]] = {}

    for path, method_map in sorted(spec["paths"].items()):
        for method, operation in sorted(method_map.items()):
            operation_id = operation["operationId"]
            tag = operation["tags"][0]
            service_module = to_snake(tag)
            service_class = f"{to_pascal(tag)}Service"
            service_attr = service_module

            method_base = operation_id
            prefix = f"{tag}_"
            if method_base.startswith(prefix):
                method_base = method_base[len(prefix) :]
            method_name = to_snake(method_base)

            seen = method_names_by_tag.setdefault(tag, set())
            if method_name in seen:
                suffix = 2
                while f"{method_name}_{suffix}" in seen:
                    suffix += 1
                method_name = f"{method_name}_{suffix}"
            seen.add(method_name)

            parameters = tuple(
                ParamSpec(
                    name=param["name"],
                    required=param.get("required", False),
                    in_=param.get("in", "query"),
                    schema_type=param.get("schema", {}).get("type", "string"),
                )
                for param in operation.get("parameters", [])
            )

            body_schema = (
                operation.get("requestBody", {})
                .get("content", {})
                .get("application/json", {})
                .get("schema", {})
            )
            has_complex_body = bool(body_schema) and any(
                key in body_schema for key in ("oneOf", "anyOf", "allOf", "$ref")
            )

            body_fields: tuple[ParamSpec, ...]
            if has_complex_body:
                body_fields = tuple()
            else:
                required_body = set(body_schema.get("required", []))
                body_fields = tuple(
                    ParamSpec(
                        name=field,
                        required=field in required_body,
                        in_="body",
                        schema_type=field_spec.get("type", "string"),
                    )
                    for field, field_spec in sorted(body_schema.get("properties", {}).items())
                )

            raw_summary = operation.get("summary") or operation.get("description") or ""
            summary = " ".join(raw_summary.split()).strip()

            all_operations.append(
                OperationSpec(
                    operation_id=operation_id,
                    method=method.upper(),
                    path=path,
                    tag=tag,
                    service_module=service_module,
                    service_class=service_class,
                    service_attr=service_attr,
                    method_name=method_name,
                    parameters=parameters,
                    body_fields=body_fields,
                    has_complex_body=has_complex_body,
                    summary=summary,
                )
            )

    return sorted(
        all_operations,
        key=lambda op: (op.service_module, op.method_name, op.path, op.method),
    )


def render_operations_module(operations: list[OperationSpec]) -> str:
    lines: list[str] = [
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass",
        "",
        "",
        "@dataclass(frozen=True)",
        "class OperationSpec:",
        "    operation_id: str",
        "    method: str",
        "    path: str",
        "    tag: str",
        "    service_module: str",
        "    service_class: str",
        "    service_attr: str",
        "    method_name: str",
        "    parameters: tuple[str, ...]",
        "    required_parameters: tuple[str, ...]",
        "    body_fields: tuple[str, ...]",
        "    required_body_fields: tuple[str, ...]",
        "    has_complex_body: bool",
        "",
        "",
        "OPERATIONS: tuple[OperationSpec, ...] = (",
    ]

    for op in operations:
        params = tuple(p.name for p in op.parameters)
        req_params = tuple(p.name for p in op.parameters if p.required)
        body = tuple(p.name for p in op.body_fields)
        req_body = tuple(p.name for p in op.body_fields if p.required)
        lines.extend(
            [
                "    OperationSpec(",
                f"        operation_id={op.operation_id!r},",
                f"        method={op.method!r},",
                f"        path={op.path!r},",
                f"        tag={op.tag!r},",
                f"        service_module={op.service_module!r},",
                f"        service_class={op.service_class!r},",
                f"        service_attr={op.service_attr!r},",
                f"        method_name={op.method_name!r},",
                f"        parameters={params!r},",
                f"        required_parameters={req_params!r},",
                f"        body_fields={body!r},",
                f"        required_body_fields={req_body!r},",
                f"        has_complex_body={op.has_complex_body!r},",
                "    ),",
            ]
        )

    lines.extend(
        [
            ")",
            "",
            "OPERATION_INDEX: dict[str, OperationSpec] = {",
            "    op.operation_id: op for op in OPERATIONS",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def _render_signature(op: OperationSpec) -> list[str]:
    lines: list[str] = ["self"]
    if op.method == "GET":
        required = [p for p in op.parameters if p.required]
        optional = [p for p in op.parameters if not p.required]
        for param in required:
            lines.append(f"{param.name}: QueryScalar")
        if optional:
            lines.append("*")
        for param in optional:
            lines.append(f"{param.name}: QueryScalar | None = None")
        return lines

    if op.has_complex_body:
        lines.append("payload: dict[str, Any]")
        return lines

    if not op.body_fields:
        return lines

    lines.append("*")
    for field in op.body_fields:
        if field.required:
            lines.append(f"{field.name}: BodyValue")
        else:
            lines.append(f"{field.name}: BodyValue | None = None")
    return lines


def _render_docstring(op: OperationSpec) -> list[str]:
    if not op.summary:
        return [f'        """``{op.method} {op.path}`` (``{op.operation_id}``)."""']
    safe_summary = op.summary.replace('"""', "'''")
    return [f'        """{safe_summary}\n\n        ``{op.method} {op.path}`` (``{op.operation_id}``).\n        """']


def _render_method(op: OperationSpec) -> str:
    signature = _render_signature(op)
    rendered_signature = [f"        {item}," for item in signature]
    docstring_lines = _render_docstring(op)

    body_lines: list[str] = []
    if op.method == "GET":
        body_lines.extend(["        params = _clean_mapping(", "            {"])
        for param in op.parameters:
            body_lines.append(f"                {param.name!r}: _coerce_query_value({param.name}),")
        body_lines.extend(
            [
                "            }",
                "        )",
                "        return self._transport.request(",
                f"            {op.method!r},",
                f"            {op.path!r},",
                "            params=params,",
                "        )",
            ]
        )
    elif op.has_complex_body:
        body_lines.extend(
            [
                "        return self._transport.request(",
                f"            {op.method!r},",
                f"            {op.path!r},",
                "            json_body=payload,",
                "        )",
            ]
        )
    elif op.body_fields:
        body_lines.extend(["        json_body = _clean_mapping(", "            {"])
        for field in op.body_fields:
            body_lines.append(f"                {field.name!r}: {field.name},")
        body_lines.extend(
            [
                "            }",
                "        )",
                "        return self._transport.request(",
                f"            {op.method!r},",
                f"            {op.path!r},",
                "            json_body=json_body,",
                "        )",
            ]
        )
    else:
        body_lines.extend(
            [
                "        return self._transport.request(",
                f"            {op.method!r},",
                f"            {op.path!r},",
                "        )",
            ]
        )

    return "\n".join(
        [
            f"    def {op.method_name}(",
            *rendered_signature,
            "    ) -> JSONReturn:",
            *docstring_lines,
            *body_lines,
            "",
        ]
    )


def render_service_module(operations: list[OperationSpec]) -> str:
    service_class = operations[0].service_class
    has_get = any(operation.method == "GET" for operation in operations)
    has_post = any(operation.method == "POST" for operation in operations)
    has_complex = any(operation.has_complex_body for operation in operations)

    helper_imports = ["JSONReturn", "_clean_mapping"]
    if has_get:
        helper_imports.append("_coerce_query_value")

    type_imports: list[str] = []
    if has_post and any(
        not operation.has_complex_body and operation.body_fields for operation in operations
    ):
        type_imports.append("BodyValue")
    if has_get:
        type_imports.append("QueryScalar")

    lines: list[str] = [
        "from __future__ import annotations",
        "",
    ]
    if has_complex:
        lines.extend(["from typing import Any", ""])

    lines.extend(
        [
            f"from getdx.helpers import {', '.join(helper_imports)}",
            "from getdx.http.transport import DXTransport",
        ]
    )

    if type_imports:
        lines.append(f"from getdx.types import {', '.join(type_imports)}")

    lines.extend(
        [
            "",
            "",
            f"class {service_class}:",
            "    def __init__(self, transport: DXTransport) -> None:",
            "        self._transport = transport",
            "",
        ]
    )

    for operation in operations:
        lines.append(_render_method(operation))

    return "\n".join(lines)


def render_services_init(operations: list[OperationSpec], *, api_name: str) -> str:
    by_module: dict[str, OperationSpec] = {}
    for operation in operations:
        by_module.setdefault(operation.service_module, operation)

    ordered = sorted(by_module.items())
    lines: list[str] = ["from __future__ import annotations", ""]

    for _, op in ordered:
        lines.append(
            f"from getdx.{api_name}.services.{op.service_module} import {op.service_class}"
        )

    lines.extend(["", "SERVICE_CLASS_BY_TAG = {"])
    for _, op in ordered:
        lines.append(f"    {op.tag!r}: {op.service_class},")
    lines.append("}")

    lines.extend(["", "__all__ = ["])
    for _, op in ordered:
        lines.append(f"    {op.service_class!r},")
    lines.extend(["]", ""])
    return "\n".join(lines)


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate DX SDK service wrappers from OpenAPI")
    parser.add_argument("--spec", default=str(DEFAULT_SPEC), help="Path to OpenAPI JSON file")
    parser.add_argument("--api-name", default="web", help="Generated API namespace name")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Root output directory (api namespace will be appended)",
    )
    args = parser.parse_args()

    spec_path = Path(args.spec)
    api_name = to_snake(args.api_name)
    output_root = Path(args.output_root)
    api_dir = output_root / api_name
    services_dir = api_dir / "services"

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    operations = load_operations(spec)

    api_dir.mkdir(parents=True, exist_ok=True)
    services_dir.mkdir(parents=True, exist_ok=True)

    write_file(
        api_dir / "operations.py",
        "# This file is auto-generated by scripts/generate_from_openapi.py\n\n"
        + render_operations_module(operations),
    )

    for tag in sorted({operation.tag for operation in operations}):
        tag_operations = [op for op in operations if op.tag == tag]
        service_module = tag_operations[0].service_module
        write_file(
            services_dir / f"{service_module}.py",
            "# This file is auto-generated by scripts/generate_from_openapi.py\n\n"
            + render_service_module(tag_operations),
        )

    write_file(
        services_dir / "__init__.py",
        "# This file is auto-generated by scripts/generate_from_openapi.py\n\n"
        + render_services_init(operations, api_name=api_name),
    )

    print(
        f"Generated {len(operations)} operations across {len({op.tag for op in operations})} tags "
        f"for '{api_name}' from {spec_path}"
    )


if __name__ == "__main__":
    main()
