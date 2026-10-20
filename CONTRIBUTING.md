# Contributing to repo-proof

Thank you for improving evidence-based repository review.

## Before opening an issue

Search existing issues first. For rule changes, include a concrete false positive or false negative and explain what evidence should change the result. Security reports belong in the private process described in [SECURITY.md](SECURITY.md).

## Development setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
```

The package has no runtime dependencies. Development checks use the standard library, with Ruff as an optional linter.

```bash
python -m unittest discover -s tests -v
python -m compileall -q src
```

## Pull requests

1. Keep one logical change per pull request.
2. Add or update evidence fixtures when a rule changes.
3. Document user-visible behavior in the README, rulebook, or changelog.
4. Explain the motivation, implementation, and validation in the pull request body.
5. Avoid scoring based on popularity alone; rules must be tied to reviewable evidence.

By contributing, you agree that your contribution is licensed under the MIT License.
