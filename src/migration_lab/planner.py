"""Validated dependency inventory and stable topological migration order."""
from __future__ import annotations

from dataclasses import dataclass
import heapq
import json
from pathlib import Path


ALLOWED_TYPES = {"table", "sequence", "type", "function", "view", "procedure", "package", "data"}


@dataclass(frozen=True)
class Step:
    name: str
    kind: str
    depends_on: tuple[str, ...]
    review_required: bool = False
    note: str = ""


def load_inventory(path: Path) -> list[Step]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict) or not isinstance(obj.get("objects"), list):
        raise ValueError("Inventory must contain an 'objects' array")
    steps: list[Step] = []
    for item in obj["objects"]:
        if not isinstance(item, dict):
            raise ValueError("Inventory entries must be objects")
        name, kind = item.get("name"), item.get("type")
        dependencies = item.get("depends_on", [])
        if not isinstance(name, str) or not name or not isinstance(kind, str) or kind not in ALLOWED_TYPES:
            raise ValueError(f"Invalid name/type for entry: {item!r}")
        if not isinstance(dependencies, list) or any(not isinstance(d, str) for d in dependencies):
            raise ValueError(f"Invalid dependencies for {name}")
        if len(dependencies) != len(set(dependencies)):
            raise ValueError(f"Duplicate dependency for {name}")
        if not isinstance(item.get("review_required", False), bool):
            raise ValueError(f"Invalid review_required for {name}")
        steps.append(Step(name, kind, tuple(dependencies), item.get("review_required", False),
                          str(item.get("note", ""))))
    return steps


def make_plan(steps: list[Step]) -> list[Step]:
    by_name = {step.name: step for step in steps}
    if len(by_name) != len(steps):
        raise ValueError("Duplicate object name in inventory")
    incoming = {name: len(step.depends_on) for name, step in by_name.items()}
    outgoing: dict[str, list[str]] = {name: [] for name in by_name}
    for step in steps:
        for dep in step.depends_on:
            if dep not in by_name:
                raise ValueError(f"Missing dependency: {step.name} -> {dep}")
            outgoing[dep].append(step.name)
    ready = [name for name, count in incoming.items() if count == 0]
    heapq.heapify(ready)
    ordered: list[Step] = []
    while ready:
        name = heapq.heappop(ready)
        ordered.append(by_name[name])
        for follower in outgoing[name]:
            incoming[follower] -= 1
            if incoming[follower] == 0:
                heapq.heappush(ready, follower)
    if len(ordered) != len(steps):
        cyclic = ", ".join(sorted(name for name, degree in incoming.items() if degree))
        raise ValueError(f"Circular dependencies involving: {cyclic}")
    return ordered


def as_dict(plan: list[Step]) -> dict:
    return {
        "plan_type": "review_only_not_executable",
        "object_count": len(plan),
        "manual_review_count": sum(step.review_required for step in plan),
        "steps": [{"order": index, "name": step.name, "type": step.kind,
                   "depends_on": list(step.depends_on), "review_required": step.review_required,
                   "note": step.note} for index, step in enumerate(plan, start=1)],
    }


def to_markdown(report: dict) -> str:
    lines = ["# Proposed Migration Dependency Order", "",
             "> Review-only plan. This file does not run DDL/DML.", "",
             "| # | Object | Type | Dependencies | Approval |", "| ---: | --- | --- | --- | --- |"]
    for s in report["steps"]:
        deps = ", ".join(f"`{d}`" for d in s["depends_on"]) or "—"
        approval = "Manual review" if s["review_required"] else "Standard verification"
        lines.append(f"| {s['order']} | `{s['name']}` | {s['type']} | {deps} | {approval} |")
    return "\n".join(lines) + "\n"
