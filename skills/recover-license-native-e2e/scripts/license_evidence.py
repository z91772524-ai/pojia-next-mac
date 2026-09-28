#!/usr/bin/env python3
"""Maintain evidence gates for native license recovery work."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
GATE_NAMES = (
    "inventory",
    "decision-trace",
    "fixture-vectors",
    "algorithm-chain",
    "protocol-trace",
    "native-acceptance",
    "clean-restart",
    "feature-smoke",
    "binary-integrity",
    "server-dependency",
    "backend-parity",
    "reproducibility",
)
PROFILE_GATES = {
    "offline": (
        "inventory",
        "decision-trace",
        "fixture-vectors",
        "algorithm-chain",
        "native-acceptance",
        "clean-restart",
        "feature-smoke",
        "binary-integrity",
        "server-dependency",
        "reproducibility",
    ),
    "server": (
        "inventory",
        "decision-trace",
        "fixture-vectors",
        "protocol-trace",
        "native-acceptance",
        "clean-restart",
        "feature-smoke",
        "binary-integrity",
        "server-dependency",
        "backend-parity",
        "reproducibility",
    ),
    "hybrid": GATE_NAMES,
}
GATE_STATUSES = ("pending", "pass", "fail", "not-applicable")


class EvidenceError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot(path_value: str | os.PathLike[str]) -> dict[str, Any]:
    path = Path(path_value).expanduser().resolve()
    if not path.exists():
        raise EvidenceError(f"Artifact does not exist: {path}")
    if path.is_file():
        stat = path.stat()
        return {
            "path": str(path),
            "kind": "file",
            "size": stat.st_size,
            "sha256": sha256_file(path),
            "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(timespec="seconds"),
        }
    if not path.is_dir():
        raise EvidenceError(f"Unsupported artifact type: {path}")

    tree_digest = hashlib.sha256()
    file_count = 0
    total_size = 0
    for child in sorted((item for item in path.rglob("*") if item.is_file()), key=lambda item: item.as_posix().lower()):
        relative = child.relative_to(path).as_posix()
        child_hash = sha256_file(child)
        child_size = child.stat().st_size
        tree_digest.update(relative.encode("utf-8"))
        tree_digest.update(b"\0")
        tree_digest.update(child_hash.encode("ascii"))
        tree_digest.update(b"\0")
        file_count += 1
        total_size += child_size
    return {
        "path": str(path),
        "kind": "directory",
        "file_count": file_count,
        "size": total_size,
        "sha256": tree_digest.hexdigest(),
    }


def workspace_path(value: str | os.PathLike[str]) -> Path:
    return Path(value).expanduser().resolve()


def state_path(workspace: Path) -> Path:
    return workspace / "state.json"


def load_state(workspace_value: str | os.PathLike[str]) -> tuple[Path, dict[str, Any]]:
    workspace = workspace_path(workspace_value)
    path = state_path(workspace)
    if not path.is_file():
        raise EvidenceError(f"Evidence workspace is not initialized: {workspace}")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"Invalid state file: {path}") from exc
    if state.get("schema_version") != SCHEMA_VERSION:
        raise EvidenceError(f"Unsupported state schema: {state.get('schema_version')!r}")
    return workspace, state


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


def save_state(workspace: Path, state: dict[str, Any]) -> None:
    state["updated_utc"] = utc_now()
    atomic_write_json(state_path(workspace), state)


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def event(state: dict[str, Any], action: str, detail: dict[str, Any]) -> None:
    state["events"].append({"time_utc": utc_now(), "action": action, "detail": detail})


def artifact_record(path: str, role: str, label: str | None = None) -> dict[str, Any]:
    record = snapshot(path)
    record.update({"role": role, "label": label or Path(path).name})
    return record


def evidence_records(paths: list[str]) -> list[dict[str, Any]]:
    return [snapshot(path) for path in paths]


def cmd_init(args: argparse.Namespace) -> int:
    workspace = workspace_path(args.workspace)
    path = state_path(workspace)
    if path.exists() and not args.force:
        raise EvidenceError(f"Workspace already initialized: {workspace}")
    for directory in ("fixtures", "traces", "outputs", "reports"):
        (workspace / directory).mkdir(parents=True, exist_ok=True)
    target = artifact_record(args.target, "original-main", "primary target")
    gates = {
        name: {"status": "pending", "note": "", "evidence": [], "updated_utc": None}
        for name in GATE_NAMES
    }
    gates["inventory"] = {
        "status": "pass",
        "note": "Primary target inventoried at workspace initialization.",
        "evidence": [target],
        "updated_utc": utc_now(),
    }
    state = {
        "schema_version": SCHEMA_VERSION,
        "created_utc": utc_now(),
        "updated_utc": utc_now(),
        "workspace": str(workspace),
        "classification": {
            "runtime": "unknown",
            "protection": "unknown",
            "authority": "unknown",
            "server_role": "unknown",
        },
        "artifacts": [target],
        "fixtures": [],
        "gates": gates,
        "events": [],
    }
    event(state, "init", {"target": target})
    save_state(workspace, state)
    emit({"success": True, "workspace": str(workspace), "target": target})
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    workspace, state = load_state(args.workspace)
    updates = {
        key: value
        for key, value in {
            "runtime": args.runtime,
            "protection": args.protection,
            "authority": args.authority,
            "server_role": args.server_role,
        }.items()
        if value is not None
    }
    if not updates:
        raise EvidenceError("No classification values were supplied")
    state["classification"].update(updates)
    event(state, "classify", updates)
    save_state(workspace, state)
    emit({"success": True, "classification": state["classification"]})
    return 0


def cmd_add_artifact(args: argparse.Namespace) -> int:
    workspace, state = load_state(args.workspace)
    record = artifact_record(args.path, args.role, args.label)
    record["id"] = f"artifact-{len(state['artifacts']) + 1:04d}"
    state["artifacts"].append(record)
    event(state, "add-artifact", record)
    save_state(workspace, state)
    emit({"success": True, "artifact": record})
    return 0


def cmd_add_fixture(args: argparse.Namespace) -> int:
    workspace, state = load_state(args.workspace)
    fixture = {
        "id": f"fixture-{len(state['fixtures']) + 1:04d}",
        "label": args.label,
        "expected": args.expected,
        "request": snapshot(args.request),
        "response": snapshot(args.response),
        "note": args.note or "",
        "recorded_utc": utc_now(),
    }
    state["fixtures"].append(fixture)
    expected_values = {item["expected"] for item in state["fixtures"]}
    if {"accepted", "rejected"}.issubset(expected_values):
        state["gates"]["fixture-vectors"] = {
            "status": "pass",
            "note": "At least one accepted and one rejected fixture are recorded.",
            "evidence": [
                {"fixture_id": item["id"], "request": item["request"], "response": item["response"]}
                for item in state["fixtures"]
            ],
            "updated_utc": utc_now(),
        }
    event(state, "add-fixture", {"id": fixture["id"], "expected": fixture["expected"]})
    save_state(workspace, state)
    emit({"success": True, "fixture": fixture, "fixture_gate": state["gates"]["fixture-vectors"]["status"]})
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    workspace, state = load_state(args.workspace)
    if args.name not in GATE_NAMES:
        raise EvidenceError(f"Unknown gate: {args.name}")
    if args.status == "pass" and not args.evidence:
        raise EvidenceError("A passing gate requires at least one evidence file or directory")
    if args.status == "not-applicable" and not args.note:
        raise EvidenceError("A not-applicable gate requires a reason in --note")
    record = {
        "status": args.status,
        "note": args.note or "",
        "evidence": evidence_records(args.evidence or []),
        "updated_utc": utc_now(),
    }
    state["gates"][args.name] = record
    event(state, "gate", {"name": args.name, "status": args.status})
    save_state(workspace, state)
    emit({"success": True, "gate": args.name, "record": record})
    return 0


def cmd_verify_integrity(args: argparse.Namespace) -> int:
    workspace, state = load_state(args.workspace)
    originals = [item for item in state["artifacts"] if item["role"].startswith("original-")]
    if not originals:
        raise EvidenceError("No original artifacts are recorded")
    rows = []
    success = True
    for original in originals:
        try:
            current = snapshot(original["path"])
            matches = current["sha256"] == original["sha256"]
            rows.append({"path": original["path"], "baseline": original["sha256"], "current": current["sha256"], "matches": matches})
            success = success and matches
        except EvidenceError as exc:
            rows.append({"path": original["path"], "baseline": original["sha256"], "error": str(exc), "matches": False})
            success = False
    report_path = workspace / "reports" / "binary-integrity.json"
    report = {"checked_utc": utc_now(), "success": success, "artifacts": rows}
    atomic_write_json(report_path, report)
    state["gates"]["binary-integrity"] = {
        "status": "pass" if success else "fail",
        "note": "All recorded originals match baseline hashes." if success else "One or more originals changed or disappeared.",
        "evidence": [snapshot(report_path)],
        "updated_utc": utc_now(),
    }
    event(state, "verify-integrity", {"success": success, "report": str(report_path)})
    save_state(workspace, state)
    emit(report)
    return 0 if success else 1


def cmd_status(args: argparse.Namespace) -> int:
    _, state = load_state(args.workspace)
    emit({
        "classification": state["classification"],
        "artifacts": len(state["artifacts"]),
        "fixtures": len(state["fixtures"]),
        "gates": {name: value["status"] for name, value in state["gates"].items()},
    })
    return 0


def snapshot_issue(record: dict[str, Any], label: str) -> str | None:
    path = record.get("path")
    expected = record.get("sha256")
    if not path or not expected:
        return f"{label}: evidence record has no path or sha256"
    try:
        current = snapshot(path)
    except EvidenceError as exc:
        return f"{label}: {exc}"
    if current["sha256"] != expected:
        return f"{label}: hash changed ({expected} -> {current['sha256']})"
    return None


def classification_issues(profile: str, classification: dict[str, str]) -> list[str]:
    issues = []
    if classification.get("runtime") in {None, "unknown"}:
        issues.append("runtime classification is unknown")
    authority = classification.get("authority")
    server_role = classification.get("server_role")
    if profile == "offline":
        if authority != "offline-client":
            issues.append(f"offline profile requires authority=offline-client, got {authority!r}")
        if server_role != "none":
            issues.append(f"offline profile requires server_role=none, got {server_role!r}")
    elif profile == "server":
        if authority not in {"server-issued", "server-executed"}:
            issues.append(f"server profile requires a server authority, got {authority!r}")
        if server_role in {None, "none", "unknown"}:
            issues.append(f"server profile requires a concrete server role, got {server_role!r}")
    elif profile == "hybrid":
        if authority != "hybrid":
            issues.append(f"hybrid profile requires authority=hybrid, got {authority!r}")
        if server_role in {None, "none", "unknown"}:
            issues.append(f"hybrid profile requires a concrete server role, got {server_role!r}")
    return issues


def cmd_check(args: argparse.Namespace) -> int:
    workspace, state = load_state(args.workspace)
    required = PROFILE_GATES[args.profile]
    statuses = {name: state["gates"][name]["status"] for name in required}
    missing = [name for name, status in statuses.items() if status != "pass"]
    evidence_issues = []
    for gate_name in required:
        if state["gates"][gate_name]["status"] != "pass":
            continue
        for index, record in enumerate(state["gates"][gate_name]["evidence"]):
            if "path" not in record:
                continue
            issue = snapshot_issue(record, f"gate {gate_name} evidence {index + 1}")
            if issue:
                evidence_issues.append(issue)
    for fixture in state["fixtures"]:
        for side in ("request", "response"):
            issue = snapshot_issue(fixture[side], f"fixture {fixture['id']} {side}")
            if issue:
                evidence_issues.append(issue)
    class_issues = classification_issues(args.profile, state["classification"])
    report = {
        "checked_utc": utc_now(),
        "profile": args.profile,
        "success": not missing and not evidence_issues and not class_issues,
        "required_gates": statuses,
        "incomplete_or_failed": missing,
        "evidence_issues": evidence_issues,
        "classification_issues": class_issues,
        "classification": state["classification"],
        "target": state["artifacts"][0],
    }
    report_path = workspace / "reports" / f"gate-report-{args.profile}.json"
    atomic_write_json(report_path, report)
    emit({**report, "report": str(report_path)})
    return 0 if report["success"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="initialize an evidence workspace")
    init.add_argument("workspace")
    init.add_argument("--target", required=True)
    init.add_argument("--force", action="store_true")
    init.set_defaults(handler=cmd_init)

    classify = subparsers.add_parser("classify", help="record runtime and authority classification")
    classify.add_argument("workspace")
    classify.add_argument("--runtime")
    classify.add_argument("--protection")
    classify.add_argument("--authority", choices=("offline-client", "server-issued", "hybrid", "server-executed", "unknown"))
    classify.add_argument("--server-role", choices=("none", "issuer", "entitlement", "content", "compute", "hybrid", "unknown"))
    classify.set_defaults(handler=cmd_classify)

    artifact = subparsers.add_parser("add-artifact", help="hash and record an artifact")
    artifact.add_argument("workspace")
    artifact.add_argument("--path", required=True)
    artifact.add_argument("--role", required=True)
    artifact.add_argument("--label")
    artifact.set_defaults(handler=cmd_add_artifact)

    fixture = subparsers.add_parser("add-fixture", help="record a request/response fixture pair")
    fixture.add_argument("workspace")
    fixture.add_argument("--request", required=True)
    fixture.add_argument("--response", required=True)
    fixture.add_argument("--expected", choices=("accepted", "rejected", "unknown"), required=True)
    fixture.add_argument("--label", required=True)
    fixture.add_argument("--note")
    fixture.set_defaults(handler=cmd_add_fixture)

    gate = subparsers.add_parser("gate", help="set a validation gate with hashed evidence")
    gate.add_argument("workspace")
    gate.add_argument("--name", choices=GATE_NAMES, required=True)
    gate.add_argument("--status", choices=GATE_STATUSES, required=True)
    gate.add_argument("--evidence", action="append", default=[])
    gate.add_argument("--note")
    gate.set_defaults(handler=cmd_gate)

    integrity = subparsers.add_parser("verify-integrity", help="compare original artifacts with baseline hashes")
    integrity.add_argument("workspace")
    integrity.set_defaults(handler=cmd_verify_integrity)

    status = subparsers.add_parser("status", help="show current gate status")
    status.add_argument("workspace")
    status.set_defaults(handler=cmd_status)

    check = subparsers.add_parser("check", help="enforce profile-specific completion gates")
    check.add_argument("workspace")
    check.add_argument("--profile", choices=tuple(PROFILE_GATES), required=True)
    check.set_defaults(handler=cmd_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return int(args.handler(args))
    except EvidenceError as exc:
        emit({"success": False, "error": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
