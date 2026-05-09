# UAT Run — ai-pr-review v0.2.0-alpha — MacBook Pro

> Copied from `docs/uat/UAT-TEMPLATE.md`. Results recorded on branch `uat/v0.2.0-alpha-macbook`.

---

## Run metadata

| Field | Value |
|---|---|
| Version | v0.2.0-alpha |
| Platform | macbook-pro |
| Tester | Stu Last |
| Date | 2026-05-09 |
| Action ref tested | `Spyced-Concepts/ai-pr-review@functional-test` |
| Provider(s) tested | anthropic, github-models |
| Test repo | Spyced-Concepts/corvex-strike |
| Branch | uat/v0.2.0-alpha-macbook |

## Result summary

| Result | Count |
|---|---|
| ✅ Pass | |
| ❌ Fail | |
| ⏭️ Skip | |

**Overall:** IN PROGRESS

---

## Prerequisites checklist

- [x] `Spyced-Concepts/corvex-strike` has `AI_API_KEY` secret configured ✓ 2026-05-09
- [x] `Spyced-Concepts/corvex-strike` `AI_MODEL` updated to `claude-sonnet-4-6` for UAT ✓ 2026-05-09 — **revert to `claude-haiku-4-5-20251001` after UAT completes**
- [x] `Spyced-Concepts/corvex-strike` has `.github/workflows/ai-review.yml` pointing at `functional-test` ✓ PR #3
- [x] Tester has access to create PRs and observe workflow runs in corvex-strike

---

## Test scenarios

### UAT-001 — Valid diff, Anthropic provider

**Setup:** corvex-strike PR #3 — migration from inline script to action.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | ✅ | 16 seconds |
| Review comment posted on PR | ✅ | Posted by github-actions[bot] |
| Comment contains `## AI Code Review` header | ✅ | No vendor branding |
| Comment ends with one of the three verdicts | ✅ | APPROVE WITH NOTES |
| `*Automated review. Maintainer approval required.*` footer present | ✅ | |

**Result:** ✅ Pass
**Notes:** Review content was high quality — correctly identified retry logic gap, truncation behaviour, and checkout step intent. No false positives.

---

### UAT-001c — Valid diff, GitHub Models (zero cost)

**Setup:** corvex-strike PR #3 — `ai_provider: github-models`, `ai_api_key: ${{ secrets.GITHUB_TOKEN }}`, `ai_model: gpt-4o`. No external API key.

**Bugs found and fixed during this scenario:**
- BUG-001: `models: read` permission required in workflow permissions block — fixed in `setup-github-models.md`
- BUG-002: GitHub Models uses `/chat/completions` not `/v1/chat/completions` — fixed by creating dedicated `github-models` adapter
- BUG-003: `importlib.import_module("adapters.github-models")` fails (hyphen invalid in Python module names) — fixed by normalising with `.replace("-", "_")` in `review.py`

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | ✅ | After 3 bug fixes; run 25609481561 |
| Review comment posted on PR | ✅ | Posted by github-actions[bot] |
| No external API key used | ✅ | GITHUB_TOKEN only |

**Result:** ✅ Pass (3 bugs found and fixed — all corrected in UAT branch)
**Notes:** Sensitive data scan ran correctly as criterion 1. GPT-4o via GitHub Models produced a well-structured review. Header `## AI Code Review` — no vendor branding.

---

### UAT-002 — Large diff truncation note

**Setup:** Set `diff_lines: 10` in the workflow to force truncation on any PR.

**Expected:** Review comment contains `> Diff was large — review based on first 10 lines only.`

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | | |
| Truncation note present in comment | | |
| Note references the correct line limit (10) | | |

**Result:**
**Notes:**

---

### UAT-003 — Missing AI_API_KEY

**Setup:** Temporarily remove the `AI_API_KEY` secret from corvex-strike. Re-run or open a new PR.

**Expected:** Workflow fails. Log contains `::error::AI_API_KEY secret not configured`.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| Error message clear and actionable | | |
| No partial review posted | | |

**Result:**
**Notes:**

---

### UAT-004 — Missing AI_MODEL

**Setup:** Remove the `AI_MODEL` variable from corvex-strike. Open a PR or re-run.

**Expected:** Workflow fails with `::error::AI_MODEL variable not configured`.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| Error message clear and actionable | | |

**Result:**
**Notes:**

---

### UAT-005 — Invalid API key

**Setup:** Set `AI_API_KEY` to `sk-ant-INVALID000000000000000000000` in corvex-strike secrets.

**Expected:** Workflow fails with HTTP 401 error visible in log.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| HTTP error code visible in log | | |
| No partial review posted | | |

**Result:**
**Notes:**

---

### UAT-006 — Unknown AI_PROVIDER value

**Setup:** Set `ai_provider: notarealai` in the workflow file temporarily.

**Expected:** Workflow fails with `::error::Unknown AI_PROVIDER 'notarealai'. Supported: anthropic, gemini, openai`.

| Check | Result | Notes |
|---|---|---|
| Workflow fails (non-zero exit) | | |
| Error lists all supported providers | | |

**Result:**
**Notes:**

---

### UAT-007 — Sensitive data detected in diff

**Setup:** Open a PR that adds a line containing a dummy key pattern, e.g.: `# TEST_KEY=sk-ant-test1234567890abcdefghijklmnop` in a comment.

**Expected:** Review flags the pattern as Critical in criterion 1 before all other findings.

| Check | Result | Notes |
|---|---|---|
| Review comment posted | | |
| Sensitive data finding in criterion 1 | | |
| Severity classified as Critical | | |
| Finding appears before other criteria | | |

**Result:**
**Notes:**

---

### UAT-008 — PR body with shell metacharacters

**Setup:** Open a PR with body text containing: `$(echo injected)` and `` `date` ``.

**Expected:** Workflow completes normally. No shell injection. Metacharacters appear safely.

| Check | Result | Notes |
|---|---|---|
| Workflow run completes without error | | |
| No unexpected shell execution in logs | | |
| Review comment posted normally | | |

**Result:**
**Notes:**

---

### UAT-009 — Custom review criteria

**Setup:** Add `review_criteria: "Check for hardcoded TODO comments"` to the workflow. Open a PR.

**Expected:** Review includes the custom criterion in its output.

| Check | Result | Notes |
|---|---|---|
| Review comment posted | | |
| Custom criterion visible in review | | |

**Result:**
**Notes:**

---

### UAT-010 — Custom sensitive data rules

**Setup:** Add `custom_rules: "CORVEX_INTERNAL"` to the workflow. Open a PR adding the string `CORVEX_INTERNAL` somewhere in the diff.

**Expected:** Sensitive data scan flags `CORVEX_INTERNAL` as a finding.

| Check | Result | Notes |
|---|---|---|
| Custom term flagged in review | | |
| Finding appears in criterion 1 section | | |

**Result:**
**Notes:**

---

## Sign-off

| Field | Value |
|---|---|
| Tester | Stu Last |
| Date | 2026-05-09 |
| Overall result | |
| Ready to merge to functional-test | |
| Notes / defects raised | |
