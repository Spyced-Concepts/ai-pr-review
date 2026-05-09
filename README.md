# ai-pr-review

A reusable GitHub Action that posts an AI-generated code review on every pull request.

**Provider-agnostic** — built-in adapters for Anthropic, OpenAI, and Gemini. Works with any OpenAI-compatible endpoint (Groq, Azure OpenAI, Mistral, Ollama). No servers, no databases, no complex setup.

> Built by [Spyced Concepts Ltd.](https://spycedconcepts.co.uk)

---

## Supported providers

| Provider | `ai_provider` value | Notes |
|---|---|---|
| Anthropic | `anthropic` | Default. Prompt caching enabled. |
| OpenAI | `openai` | Also works with Groq, Azure OpenAI, Mistral, Ollama via `ai_base_url` |
| Google Gemini | `gemini` | — |

Provider-specific setup guides are in [`docs/`](docs/).

---

## Quick start

### 1. Add repository settings

| Type | Name | Value |
|---|---|---|
| Secret | `AI_API_KEY` | Your AI provider API key |
| Variable | `AI_MODEL` | Model identifier (see provider docs) |

### 2. Add the workflow

```yaml
# .github/workflows/ai-review.yml
name: AI PR Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: Spyced-Concepts/ai-pr-review@v1
        with:
          ai_api_key:   ${{ secrets.AI_API_KEY }}
          ai_model:     ${{ vars.AI_MODEL }}
          ai_provider:  anthropic        # or: openai, gemini
          pr_number:    ${{ github.event.pull_request.number }}
          pr_title:     ${{ github.event.pull_request.title }}
          pr_body:      ${{ github.event.pull_request.body }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

See [`docs/setup-anthropic.md`](docs/setup-anthropic.md), [`docs/setup-openai.md`](docs/setup-openai.md), or [`docs/setup-gemini.md`](docs/setup-gemini.md) for full setup instructions.

---

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `ai_api_key` | ✓ | — | Your AI provider API key (store as a secret) |
| `ai_model` | ✓ | — | Model identifier — see provider docs |
| `ai_provider` | | `anthropic` | Adapter: `anthropic`, `openai`, or `gemini` |
| `ai_base_url` | | `""` | Base URL override for OpenAI-compatible endpoints |
| `pr_number` | ✓ | — | Pull request number |
| `pr_title` | ✓ | — | Pull request title |
| `pr_body` | | `""` | Pull request description |
| `diff_lines` | | `1500` | Max diff lines to review |
| `review_criteria` | | `""` | Additional review criteria, one per line |
| `custom_rules` | | `""` | Custom sensitive data scan rules, one per line |
| `github_token` | ✓ | — | GitHub token for posting the review comment |

## Outputs

| Output | Description |
|---|---|
| `review` | The full review text posted as a PR comment |

---

## Review criteria

Every review checks:

1. **Sensitive data disclosure** — credentials, personal identifiers, private paths, computer/host names (always reported first)
2. **Merge conflicts** — immediate blocker
3. **Correctness** — edge cases, logic errors
4. **Cross-platform compatibility** — macOS, Linux, Windows (Git Bash)
5. **Bash quality** — `set -euo pipefail`, quoting, portability
6. **Security** — injection risks, unsafe variable expansion
7. **Code quality** — magic values, code smells, correct approach
8. **Dependencies** — external modules flagged
9. **Documentation** — docs updated alongside code
10. **PR scope** — single concern?

Add custom criteria via `review_criteria`. Add domain-specific sensitive data patterns via `custom_rules`.

---

## Security

See [SECURITY.md](SECURITY.md). In brief:

- Pin to a release tag (`@v1`) rather than `@main`
- API keys are sourced from secrets and never logged
- Review body posted via `--body-file`; no shell interpolation of review text
- The action never pushes, merges, or modifies repository settings

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). To add a new provider, implement `call_api()` in `scripts/adapters/<provider>.py` — the adapter interface is documented there.

---

## Licence

MIT — see [LICENSE](LICENSE).

Governing law: England and Wales.

Made by [Spyced Concepts Ltd.](https://spycedconcepts.co.uk)
