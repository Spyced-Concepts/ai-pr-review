# ai-pr-review

A reusable GitHub Action that posts an AI-generated code review on every pull request.

Provider-agnostic — works with any AI that accepts an API key and model identifier. Default implementation uses [Anthropic Claude](https://anthropic.com). Adapting to another provider requires changing one function in `scripts/review.py`.

> Built by [Spyced Concepts Ltd.](https://spycedconcepts.co.uk)

---

## Usage

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
          pr_number:    ${{ github.event.pull_request.number }}
          pr_title:     ${{ github.event.pull_request.title }}
          pr_body:      ${{ github.event.pull_request.body }}
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

---

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `ai_api_key` | ✓ | — | Your AI provider API key (store as a secret) |
| `ai_model` | ✓ | — | Model identifier (e.g. `claude-sonnet-4-6`) |
| `pr_number` | ✓ | — | Pull request number |
| `pr_title` | ✓ | — | Pull request title |
| `pr_body` | | `""` | Pull request description |
| `github_token` | ✓ | — | GitHub token for posting the review comment |
| `diff_lines` | | `1500` | Max diff lines to review |
| `review_criteria` | | `""` | Additional review criteria (one per line) |

## Outputs

| Output | Description |
|---|---|
| `review` | The full review text posted as a PR comment |

---

## Repository configuration

Add these to your GitHub repository settings:

| Type | Name | Value |
|---|---|---|
| Secret | `AI_API_KEY` | Your AI provider API key |
| Variable | `AI_MODEL` | Model identifier (e.g. `claude-sonnet-4-6`) |

---

## Using a different AI provider

The default implementation calls the Anthropic Claude API. To use a different provider:

1. Fork this repo
2. Edit `scripts/review.py` — find the `call_api()` function
3. Replace the Anthropic API call with your provider's equivalent
4. Update `AI_API_KEY` and `AI_MODEL` in your repository settings

The rest of the action (diff capture, prompt construction, comment posting) is provider-neutral and requires no changes.

---

## Review criteria

Every review covers:

1. Merge conflicts — immediate blocker if conflict markers found
2. Correctness — edge cases, logic errors
3. Cross-platform compatibility
4. Bash quality — `set -euo pipefail`, quoting, portability
5. Security — hardcoded secrets, injection risks
6. Code quality — magic values, code smells, correct approach
7. Dependencies — external modules flagged
8. Documentation — docs updated alongside code
9. PR scope — single concern?

Add custom criteria via the `review_criteria` input.

---

## Licence

MIT — see [LICENSE](LICENSE).

Governing law: England and Wales.

Made by [Spyced Concepts Ltd.](https://spycedconcepts.co.uk)
