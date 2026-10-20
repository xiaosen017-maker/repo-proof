from __future__ import annotations

import re
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from .models import AuditReport, CheckResult, require_manifest


SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _check(
    code: str,
    title: str,
    passed: bool,
    points: int,
    evidence: str,
    *,
    critical: bool = False,
    warning: bool = False,
) -> CheckResult:
    status = "pass" if passed else ("warn" if warning else "fail")
    return CheckResult(
        code=code,
        title=title,
        status=status,
        points=points if passed else 0,
        max_points=points,
        evidence=evidence,
        critical=critical,
    )


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def audit_manifest(manifest: dict[str, Any], *, now: datetime | None = None) -> AuditReport:
    """Evaluate a collected manifest with deterministic, explainable rules."""
    root = require_manifest(manifest)
    snapshot = root["snapshot"]
    repo = root["repository"]
    milestone = root["milestone"]
    checks: list[CheckResult] = []

    sha = str(snapshot.get("sha", "")).lower()
    checks.append(_check(
        "snapshot.full_sha", "Snapshot uses a full commit SHA", bool(SHA_RE.fullmatch(sha)), 12,
        sha or "missing", critical=True,
    ))

    is_public = repo.get("visibility") == "public"
    checks.append(_check(
        "repo.public", "Repository is publicly accessible", is_public, 10,
        f"visibility={repo.get('visibility', 'missing')}", critical=True,
    ))
    archived = bool(repo.get("archived", False))
    checks.append(_check(
        "repo.active", "Repository is not archived", not archived, 6,
        f"archived={archived}", critical=True,
    ))

    license_id = repo.get("license_spdx")
    has_license = isinstance(license_id, str) and license_id not in {"", "NOASSERTION", "OTHER"}
    checks.append(_check(
        "repo.license", "Repository has an identifiable license", has_license, 8,
        f"license={license_id or 'missing'}", critical=True,
    ))

    readme_chars = int(repo.get("readme_chars") or 0)
    checks.append(_check(
        "repo.readme", "README provides substantial project guidance", readme_chars >= 800, 10,
        f"readme_chars={readme_chars}", critical=True,
    ))
    checks.append(_check(
        "repo.docs", "Documentation is present", bool(repo.get("has_docs")), 5,
        f"has_docs={bool(repo.get('has_docs'))}", warning=True,
    ))
    checks.append(_check(
        "repo.tests", "Automated tests are present", bool(repo.get("has_tests")), 10,
        f"has_tests={bool(repo.get('has_tests'))}", warning=True,
    ))
    checks.append(_check(
        "repo.ci", "Continuous integration is configured", int(repo.get("workflow_count") or 0) > 0, 8,
        f"workflow_count={int(repo.get('workflow_count') or 0)}", warning=True,
    ))

    clock = now or datetime.now(UTC)
    pushed = _parse_time(repo.get("pushed_at"))
    days = (clock - pushed).days if pushed else None
    recent = days is not None and days <= 180
    checks.append(_check(
        "repo.recent_activity", "Repository has recent development activity", recent, 6,
        f"days_since_push={days if days is not None else 'unknown'}", warning=True,
    ))

    title = str(milestone.get("title") or "").strip()
    description = str(milestone.get("description") or "").strip()
    checks.append(_check(
        "milestone.defined", "Milestone has a clear title and description", len(title) >= 5 and len(description) >= 120, 8,
        f"title_chars={len(title)}, description_chars={len(description)}", critical=True,
    ))

    issue_count = int(milestone.get("issue_count") or 0)
    pr_count = int(milestone.get("pull_request_count") or 0)
    checks.append(_check(
        "milestone.linked_work", "Milestone links issues and pull requests", issue_count >= 2 and pr_count >= 1, 8,
        f"issues={issue_count}, pull_requests={pr_count}", critical=True,
    ))

    acceptance = int(milestone.get("acceptance_criteria_count") or 0)
    checks.append(_check(
        "milestone.acceptance", "Milestone includes verifiable acceptance criteria", acceptance >= 2, 9,
        f"acceptance_criteria_count={acceptance}", critical=True,
    ))

    max_score = sum(check.max_points for check in checks)
    score = sum(check.points for check in checks)
    critical_failures = tuple(check.code for check in checks if check.critical and check.status == "fail")
    ratio = score / max_score if max_score else 0
    if critical_failures or ratio < 0.60:
        decision = "reject"
    elif ratio < 0.80:
        decision = "review"
    else:
        decision = "accept"
    return AuditReport(score, max_score, decision, critical_failures, tuple(checks))
