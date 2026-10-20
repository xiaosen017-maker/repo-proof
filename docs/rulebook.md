# Rulebook

The rules are designed for evidence collection rather than popularity ranking. Star counts, forks, and social attention are deliberately excluded from the score.

## Critical gates

Critical gates answer whether the submission can be reviewed reliably.

| Code | Requirement | Reason |
|---|---|---|
| `snapshot.full_sha` | A lowercase 40-character commit SHA | Branches and tags can move; a commit SHA fixes the reviewed state. |
| `repo.public` | Public repository visibility | Reviewers must be able to reopen every source link. |
| `repo.active` | Repository is not archived | Archived code may be useful, but is a poor source of current development work. |
| `repo.license` | Recognizable SPDX license | A clear license is required for safe reuse and inspection. |
| `repo.readme` | At least 800 README characters | A viable project should explain its purpose, setup, and use. |
| `milestone.defined` | Specific title and substantial description | A label without scope cannot define a coding task. |
| `milestone.linked_work` | At least two issues and one pull request | The milestone needs traceable planning and implementation evidence. |
| `milestone.acceptance` | At least two checklist criteria | Reviewers need observable completion conditions. |

## Quality signals

Documentation, automated tests, continuous integration, and recent activity add confidence but do not individually reject a repository. The report marks missing signals as warnings so a reviewer can consider project-specific context.

## Thresholds

- **Accept:** no critical failures and a score of at least 80 percent.
- **Review:** no critical failures and a score from 60 through 79 percent.
- **Reject:** any critical failure or a score below 60 percent.

Thresholds are versioned with the code. A report records every rule outcome, so a future change does not erase the reasoning behind an earlier decision.
