#!/usr/bin/env python3
"""Execute a short Python probe inside a process with an embedded CPython DLL."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except OSError:
            pass
        raise


def build_javascript(code: str, requested_module: str | None) -> str:
    return f"""
setImmediate(function () {{
  try {{
    const requested = {json.dumps(requested_module or "")};
    const modules = Process.enumerateModules();
    let pythonModule = null;
    if (requested) {{
      pythonModule = modules.find(m => m.name.toLowerCase() === requested.toLowerCase());
    }} else {{
      pythonModule = modules.find(m => /^python3[0-9]+\\.dll$/i.test(m.name));
    }}
    if (pythonModule === null) {{
      send({{ kind: "fatal", error: "No loaded python3*.dll module was found" }});
      return;
    }}
    const run = new NativeFunction(pythonModule.getExportByName("PyRun_SimpleString"), "int", ["pointer"]);
    const ensure = new NativeFunction(pythonModule.getExportByName("PyGILState_Ensure"), "int", []);
    const release = new NativeFunction(pythonModule.getExportByName("PyGILState_Release"), "void", ["int"]);
    const source = Memory.allocUtf8String({json.dumps(code)});
    const state = ensure();
    let rc = -1;
    try {{
      rc = run(source);
    }} finally {{
      release(state);
    }}
    send({{ kind: "result", rc: rc, python_module: pythonModule.name }});
  }} catch (error) {{
    send({{ kind: "fatal", error: String(error), stack: error.stack || "" }});
  }}
}});
"""


def execute(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    try:
        import frida
    except ImportError as exc:
        result = {"success": False, "error": "The frida Python package is not installed"}
        return 2, result

    code = args.code
    if args.code_file:
        code = Path(args.code_file).read_text(encoding="utf-8")
    assert code is not None

    messages: list[dict[str, Any]] = []
    completed = threading.Event()
    final_payload: dict[str, Any] | None = None

    def on_message(message: dict[str, Any], _data: bytes | None) -> None:
        nonlocal final_payload
        messages.append(message)
        if message.get("type") == "send":
            payload = message.get("payload")
            if isinstance(payload, dict) and payload.get("kind") in {"result", "fatal"}:
                final_payload = payload
                completed.set()
        elif message.get("type") == "error":
            final_payload = {"kind": "fatal", "error": message.get("description", "Frida script error"), "stack": message.get("stack", "")}
            completed.set()

    session = None
    try:
        session = frida.attach(args.pid)
        script = session.create_script(build_javascript(code, args.python_module))
        script.on("message", on_message)
        script.load()
        finished = completed.wait(args.timeout)
        if not finished:
            result = {
                "success": False,
                "pid": args.pid,
                "error": f"Probe timed out after {args.timeout} seconds",
                "messages": messages,
            }
            return 3, result
        assert final_payload is not None
        success = final_payload.get("kind") == "result" and final_payload.get("rc") == 0
        result = {
            "success": success,
            "pid": args.pid,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "payload": final_payload,
            "messages": messages,
        }
        return (0 if success else 1), result
    except BaseException as exc:
        return 1, {"success": False, "pid": args.pid, "error": f"{type(exc).__name__}: {exc}", "messages": messages}
    finally:
        if session is not None:
            try:
                session.detach()
            except BaseException:
                pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--code")
    source.add_argument("--code-file")
    parser.add_argument("--python-module", help="exact loaded DLL name, for example python312.dll")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    exit_code, result = execute(args)
    if args.report:
        atomic_write_json(Path(args.report).expanduser().resolve(), result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
