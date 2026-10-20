from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


Status = Literal["pass", "warn", "fail"]


@dataclass(frozen=True)
class CheckResult:
    code: str
    title: str
    status: Status
    points: int
    max_points: int
    evidence: str
    critical: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AuditReport:
    score: int
    max_score: int
    decision: Literal["accept", "review", "reject"]
    critical_failures: tuple[str, ...]
    checks: tuple[CheckResult, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "max_score": self.max_score,
            "decision": self.decision,
            "critical_failures": list(self.critical_failures),
            "checks": [check.to_dict() for check in self.checks],
        }


def require_mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def require_manifest(value: Any) -> dict[str, Any]:
    root = require_mapping(value, "manifest")
    if root.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    for field in ("source", "snapshot", "repository", "milestone"):
        require_mapping(root.get(field), field)
    return root
