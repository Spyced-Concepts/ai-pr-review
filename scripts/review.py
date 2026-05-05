"""
AI PR review script for the ai-pr-review GitHub Action.

Reads the PR diff from $RUNNER_TEMP/pr_diff.txt, calls the configured AI
provider API, and writes the review to GITHUB_OUTPUT.

Provider: Anthropic Claude (default). To use a different provider, adapt
the API call in the `call_api()` function below to match that provider's
request format and authentication scheme.

Environment variables (set by action.yml):
    AI_API_KEY       — provider API key (from repository secret)
    AI_MODEL         — model identifier (from repository variable)
    PR_TITLE         — pull request title
    PR_BODY          — pull request description (may be empty)
    PR_NUMBER        — pull request number
    REVIEW_CRITERIA  — additional criteria lines (optional)
    DIFF_LINES_LIMIT — max lines captured (for truncation note)
"""

import json
import os
import sys
import urllib.request
import urllib.error

# ── Configuration ─────────────────────────────────────────────────────────────

API_KEY  = os.environ.get("AI_API_KEY", "")
MODEL    = os.environ.get("AI_MODEL", "")
PR_TITLE = os.environ.get("PR_TITLE", "")
PR_BODY  = os.environ.get("PR_BODY", "")
PR_NUM   = os.environ.get("PR_NUMBER", "")
EXTRA    = os.environ.get("REVIEW_CRITERIA", "")

if not API_KEY:
    print("::error::AI_API_KEY secret not configured")
    sys.exit(1)
if not MODEL:
    print("::error::AI_MODEL variable not configured")
    sys.exit(1)

# ── Load diff ─────────────────────────────────────────────────────────────────

runner_temp = os.environ.get("RUNNER_TEMP", "/tmp")
diff_path   = os.path.join(runner_temp, "pr_diff.txt")

if not os.path.exists(diff_path):
    print(f"::error::Diff file not found at {diff_path}")
    sys.exit(1)

with open(diff_path, encoding="utf-8") as f:
    diff = f.read()

# ── Build prompt ──────────────────────────────────────────────────────────────

SYSTEM = (
    "You are an expert code reviewer. Review pull request diffs thoroughly, "
    "flag genuine issues clearly, and be concise. Distinguish blockers from "
    "minor observations. Never invent issues that are not present in the diff."
)

body_excerpt = PR_BODY[:500] if PR_BODY else "(no description)"
diff_block   = diff.strip() if diff.strip() else "(empty diff)"

criteria = [
    "1. **Merge conflicts** — flag any conflict markers (<<<<<<, =======, >>>>>>>) as an immediate blocker.",
    "2. **Correctness** — does the code do what it claims? Are edge cases handled?",
    "3. **Cross-platform** — will it work on macOS, Linux, and Windows (Git Bash)?",
    "4. **Bash quality** — set -euo pipefail, quoting, portability, no bashisms.",
    "5. **Security** — no hardcoded secrets, no path injection, no unsafe variable expansion.",
    "6. **Code quality** — no magic numbers or strings, no code smells, correct approach.",
    "7. **Dependencies** — no unnecessary external modules; flag anything not from stdlib.",
    "8. **Documentation** — relevant docs updated alongside code changes.",
    "9. **PR scope** — single concern, or should it be split?",
]

if EXTRA:
    for i, line in enumerate(EXTRA.strip().splitlines(), start=len(criteria) + 1):
        if line.strip():
            criteria.append(f"{i}. {line.strip()}")

USER = (
    f"PR #{PR_NUM}: {PR_TITLE}\n\n"
    f"{body_excerpt}\n\n"
    "Diff:\n```diff\n"
    f"{diff_block}\n```\n\n"
    "Review against these criteria:\n"
    + "\n".join(criteria)
    + "\n\nEnd with exactly one of:\nAPPROVE\nAPPROVE WITH NOTES\nREQUEST CHANGES"
)

# ── Call API ──────────────────────────────────────────────────────────────────
# Default provider: Anthropic Claude.
# To use a different provider, replace this function with the appropriate
# API call for that provider. The function must return the review text as
# a string, or raise an exception on failure.

def call_api(api_key, model, system, user):
    payload = {
        "model": model,
        "max_tokens": 1024,
        "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
        "messages": [{"role": "user", "content": user}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": "prompt-caching-2024-07-31",
            "content-type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

try:
    data    = call_api(API_KEY, MODEL, SYSTEM, USER)
    content = data.get("content", [])
    if not content or content[0].get("type") != "text":
        print("::error::Unexpected API response structure")
        sys.exit(1)
    review = content[0]["text"]
except urllib.error.HTTPError as e:
    print(f"::error::API HTTP error {e.code}: {e.read().decode()}")
    sys.exit(1)
except urllib.error.URLError as e:
    print(f"::error::Network error reaching AI API: {e.reason}")
    sys.exit(1)

# ── Write output ──────────────────────────────────────────────────────────────

delimiter = "AI_REVIEW_EOF"
with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as out:
    out.write(f"review<<{delimiter}\n{review}\n{delimiter}\n")

print("Review complete.")
