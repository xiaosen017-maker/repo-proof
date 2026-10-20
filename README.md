# repo-proof

[![Quality checks](https://github.com/xiaosen017-maker/repo-proof/actions/workflows/quality.yml/badge.svg)](https://github.com/xiaosen017-maker/repo-proof/actions/workflows/quality.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB)](https://www.python.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-2EA44F)](LICENSE)

Evidence-first quality checks for GitHub repository snapshots and development milestones.

`repo-proof` collects a compact manifest from the GitHub REST API, pins the repository to a full commit SHA, and evaluates repository and milestone evidence with deterministic rules. Every result includes a code, score, and human-readable reason, so reviewers can reproduce the decision instead of trusting an opaque number.

## Why this exists

Repository selection often collapses into star counts or visual polish. Those signals do not prove that a snapshot is reproducible, a license is usable, a milestone has a coherent boundary, or completed work has acceptance evidence. `repo-proof` focuses on those facts.

## Features

- pins the default branch to a 40-character commit SHA;
- checks public access, archive state, license, README, docs, tests, CI, and recent activity;
- checks milestone description, linked issues and pull requests, and acceptance criteria;
- separates critical gates from scored quality signals;
- emits Markdown for human review or JSON for downstream automation;
- uses the Python standard library at runtime.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

Collect evidence for milestone `3`:

```bash
repo-proof collect owner/project --milestone 3 --output manifest.json
```

Public API requests work without a token at GitHub's unauthenticated rate limit. For regular use, set `GITHUB_TOKEN` to a fine-grained read-only token.

Audit the manifest:

```bash
repo-proof audit manifest.json --format markdown --output audit.md
repo-proof audit manifest.json --format json
```

Exit codes are stable: `0` for accepted evidence, `2` for review or rejection, and `1` for invalid input or collection errors.

## Decision model

Critical failures always reject a candidate. They include an invalid snapshot SHA, private or archived access, a missing recognizable license, an insubstantial README, an undefined milestone, missing linked work, or missing acceptance criteria. Noncritical checks influence the score and expose areas for manual review.

| Decision | Condition |
|---|---|
| Accept | No critical failures and at least 80 percent of available points |
| Review | No critical failures and 60 to 79 percent |
| Reject | Any critical failure or less than 60 percent |

The full rule rationale is documented in [docs/rulebook.md](docs/rulebook.md).

## Manifest contract

The manifest is intentionally small and reviewable. It records source URLs, collection time, default branch, full SHA, repository evidence, and milestone evidence. See [examples/healthy.json](examples/healthy.json) and [docs/architecture.md](docs/architecture.md).

## Project structure

```text
src/repo_proof/   collector, rules, report rendering, CLI
tests/            deterministic unit and CLI tests
docs/             architecture and rule rationale
examples/         healthy and risky manifests
.github/          CI, issue forms, and pull request template
```

## Scope and limitations

The tool supports GitHub repositories and one milestone at a time. It checks evidence availability and consistency; it does not decide whether the underlying product idea is commercially valuable, detect copied code, or replace human code review. GitHub API availability and permissions can limit collection.

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Report security issues using the process in [SECURITY.md](SECURITY.md), rather than a public issue.

## License

MIT. See [LICENSE](LICENSE).
