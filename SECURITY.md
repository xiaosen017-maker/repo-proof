# Security policy

## Supported versions

Security fixes are applied to the latest release on the default branch.

## Reporting a vulnerability

Do not open a public issue for vulnerabilities involving token exposure, unsafe URL handling, or unintended access to private repository data. Use GitHub's private vulnerability reporting feature for this repository. Include reproduction steps, affected version, impact, and a suggested mitigation when possible.

The project never writes a GitHub token to a manifest or report. Use a fine-grained read-only token and provide it through the `GITHUB_TOKEN` environment variable.
