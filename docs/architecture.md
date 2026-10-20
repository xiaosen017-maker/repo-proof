# Architecture

`repo-proof` separates collection from evaluation so the evidence can be archived, reviewed, and re-audited without another network request.

```text
GitHub REST API
      |
      v
collector (github.py) ---> versioned JSON manifest
                                  |
                                  v
                         deterministic rules
                                  |
                                  v
                      Markdown or JSON report
```

## Collection boundary

The collector requests repository metadata, the default branch head, README metadata, workflow count, a milestone, and all work items assigned to that milestone. Common `docs` and `tests` paths are probed as evidence signals. Authentication is optional and read-only access is sufficient.

## Evaluation boundary

The audit module has no network access. It validates the manifest schema, runs small explainable rules, totals points, and applies critical gates. Supplying `now` to `audit_manifest` makes time-dependent checks deterministic in tests.

## Output boundary

The renderer converts the report model to Markdown. JSON output uses the same model, so automation and human review cannot silently diverge.

## Extension points

- add a collector for another forge while preserving the manifest contract;
- introduce new schema versions instead of changing existing evidence meaning;
- add rules as pure functions with stable codes;
- add an output renderer without changing collection or scoring.
