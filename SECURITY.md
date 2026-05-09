# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| Latest release on `main` | ✅ |
| Older releases | ✗ — update to the latest release |

## Reporting a vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

To report a vulnerability, email: **security@spycedconcepts.co.uk**

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested remediation

We will acknowledge your report within 48 hours and aim to release a fix within 7 days for critical issues.

## Security design notes

This action is designed with the following principles:

- **No secrets in code** — API keys are sourced exclusively from repository secrets; never logged or written to any output
- **No shell interpolation of user content** — PR title, body, and review text are passed as environment variables to Python, not shell-interpolated
- **Review posted via file** — the review body is written to a temp file and posted with `--body-file`; no `echo "$REVIEW"` pipe that could be exploited by metacharacters in the review text
- **stdlib only** — no external Python dependencies on the runner; reduces supply chain risk
- **Read-only GitHub token** — the action only needs `pull-requests: write` and `contents: read`; it never pushes, merges, or modifies repository settings
- **Adapter isolation** — provider-specific code is contained in `scripts/adapters/`; the core `review.py` has no AI-vendor references and no outbound network calls

## Pinning the action version

We strongly recommend pinning to a specific release tag rather than `@main`:

```yaml
# Recommended — pin to a release tag
- uses: Spyced-Concepts/ai-pr-review@v1

# Also acceptable — pin to a specific commit SHA for maximum supply-chain security
- uses: Spyced-Concepts/ai-pr-review@<commit-sha>

# Not recommended — tracks moving HEAD
- uses: Spyced-Concepts/ai-pr-review@main
```

Release tags are signed commits. Check the [releases page](https://github.com/Spyced-Concepts/ai-pr-review/releases) for the latest stable version.
