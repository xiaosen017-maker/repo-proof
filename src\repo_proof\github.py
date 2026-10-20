from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from typing import Any


API_ROOT = "https://api.github.com"


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: float = 20.0) -> None:
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout

    def get(self, path: str, *, optional: bool = False) -> Any:
        request = urllib.request.Request(API_ROOT + path)
        request.add_header("Accept", "application/vnd.github+json")
        request.add_header("X-GitHub-Api-Version", "2022-11-28")
        request.add_header("User-Agent", "repo-proof/0.1")
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if optional and exc.code == 404:
                return None
            raise RuntimeError(f"GitHub API returned HTTP {exc.code} for {path}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"GitHub API request failed for {path}: {exc.reason}") from exc


def _content_exists(client: GitHubClient, repo: str, paths: tuple[str, ...]) -> bool:
    quoted_repo = "/".join(urllib.parse.quote(part, safe="") for part in repo.split("/"))
    return any(client.get(f"/repos/{quoted_repo}/contents/{path}", optional=True) is not None for path in paths)


def collect_manifest(repository: str, milestone_number: int, *, client: GitHubClient | None = None) -> dict[str, Any]:
    """Collect a compact evidence manifest from the GitHub REST API."""
    if repository.count("/") != 1:
        raise ValueError("repository must use owner/name format")
    gh = client or GitHubClient()
    owner, name = repository.split("/", 1)
    repo_path = f"/repos/{urllib.parse.quote(owner, safe='')}/{urllib.parse.quote(name, safe='')}"
    repo = gh.get(repo_path)
    branch = gh.get(f"{repo_path}/branches/{urllib.parse.quote(repo['default_branch'], safe='')}")
    readme = gh.get(f"{repo_path}/readme", optional=True)
    workflows = gh.get(f"{repo_path}/actions/workflows", optional=True) or {"total_count": 0}
    milestone = gh.get(f"{repo_path}/milestones/{milestone_number}")
    issues = gh.get(f"{repo_path}/issues?milestone={milestone_number}&state=all&per_page=100")

    issue_count = sum(1 for item in issues if "pull_request" not in item)
    pr_count = sum(1 for item in issues if "pull_request" in item)
    description = milestone.get("description") or ""
    acceptance_count = sum(
        1 for line in description.splitlines()
        if line.strip().lower().startswith(("- [ ]", "- [x]", "* [ ]", "* [x]"))
    )

    return {
        "schema_version": 1,
        "collected_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "source": {
            "provider": "github",
            "repository_url": repo["html_url"],
            "milestone_url": milestone["html_url"],
        },
        "snapshot": {
            "default_branch": repo["default_branch"],
            "sha": branch["commit"]["sha"],
        },
        "repository": {
            "full_name": repo["full_name"],
            "visibility": repo.get("visibility", "private" if repo.get("private") else "public"),
            "archived": repo.get("archived", False),
            "license_spdx": (repo.get("license") or {}).get("spdx_id"),
            "readme_chars": int((readme or {}).get("size") or 0),
            "has_docs": _content_exists(gh, repository, ("docs", "documentation")),
            "has_tests": _content_exists(gh, repository, ("tests", "test", "spec")),
            "workflow_count": int(workflows.get("total_count") or 0),
            "created_at": repo.get("created_at"),
            "pushed_at": repo.get("pushed_at"),
        },
        "milestone": {
            "number": milestone["number"],
            "title": milestone.get("title") or "",
            "description": description,
            "state": milestone.get("state"),
            "due_on": milestone.get("due_on"),
            "issue_count": issue_count,
            "pull_request_count": pr_count,
            "acceptance_criteria_count": acceptance_count,
        },
    }
