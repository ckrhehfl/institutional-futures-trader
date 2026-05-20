---
title: AI Review Gate model routing must be deterministic and fail closed
date: 2026-05-20
category: docs/solutions/security-issues
module: AI Review Gate
problem_type: security_issue
component: development_workflow
symptoms:
  - "AI Review Gate cost control needs explicit model and effort selection without weakening required-check safety."
  - "Changed-file metadata from GitHub can be paginated or include rename paths that are easy to miss."
  - "PR-derived labels and filenames can reach GitHub Actions outputs if routing logic is not sanitized."
  - "High-risk review must not silently fall back to a cheaper model when the stronger model is unavailable."
root_cause: missing_workflow_step
resolution_type: workflow_improvement
severity: high
tags: [ai-review-gate, model-routing, github-actions, cost-control, required-check]
---

# AI Review Gate model routing must be deterministic and fail closed

## Problem

PR #20 added model routing to AI Review Gate so OpenAI API cost becomes more predictable. The durable risk is that cost control can accidentally become safety reduction if the gate lets an AI choose its own model, misclassifies high-risk PRs, or quietly falls back to a weaker model when a stronger model is unavailable.

## Symptoms

- The AI Review Gate previously relied on Codex Action default model and effort settings, making cost hard to predict.
- The gate needed cheaper routing for routine and docs-only PRs while preserving stronger review for workflow, policy, secret, exchange, risk, and live-boundary changes.
- Review surfaced that GitHub PR files API pagination cannot be treated as a single JSON document unless it is explicitly slurped and flattened.
- Review surfaced that high-risk path detection must inspect both `filename` and `previous_filename`, and must include nested `.env*` files and nested `AGENTS.md` files.
- Routing metadata such as filenames, labels, and reasons can be PR-derived and must be sanitized before writing to `GITHUB_OUTPUT`.

## What Didn't Work

- Letting the model decide which model or effort to use would make cost and safety non-deterministic.
- Using a cheap fallback when the high-risk model is unavailable would hide a policy failure behind a green check.
- Treating docs-only as always low-risk is too broad because trusted gate and policy documents are themselves high-risk review inputs.
- Parsing `gh api --paginate` output directly with `json.loads` is brittle because multiple pages may not form one JSON document.
- Checking only current file paths misses rename attacks or policy movement through `previous_filename`.

## Solution

Make model routing a deterministic workflow step before the Codex invocation:

- Compute `risk_tier`, `codex_model`, `codex_effort`, and `risk_reason` from GitHub API metadata only.
- Use PR labels, changed-file metadata, `filename`, `previous_filename`, base/head repository metadata, and diff availability as routing inputs.
- Keep routing in shell/Python JSON logic, not in model reasoning.
- Route low-risk docs-only changes to `gpt-5.4-mini` with low effort when every changed file is `docs/**` or `*.md` and none are trusted policy/gate paths.
- Route default source/test/domain changes without high-risk paths to `gpt-5.4-mini` with medium effort.
- Route workflow, prompt, policy, secret, credential, adapter, exchange, OMS, Risk, and live-boundary changes to `gpt-5.3-codex` with high effort.
- Do not use nano models as the sole judge for a required AI Gate.
- If the high-risk model is unavailable, fail closed or require owner policy rather than silently choosing a cheaper model.
- Use `gh api --paginate --slurp` or an equivalent safe collector, then flatten page arrays before inspecting file metadata.
- Sanitize PR-derived `filename`, `label`, and `risk_reason` values before writing them to `GITHUB_OUTPUT`.

## Why This Works

Deterministic routing separates cost policy from model judgment. The workflow decides what level of review a PR needs from observable repository metadata, then the selected model reviews the diff under that fixed policy. This keeps the required check auditable: each run records the tier, model, effort, and reason in the job summary and JSON artifact.

Failing closed preserves the security boundary. A high-risk PR that cannot access the stronger model should not become a low-cost review by accident. It should surface as `NEEDS_OWNER_POLICY` or another blocking failure that a human owner can resolve.

Pagination and output sanitization matter because the router itself is part of the gate. If the file list is truncated or malformed, high-risk paths can be missed. If PR-derived strings are written to `GITHUB_OUTPUT` without sanitization, a malicious filename or label can interfere with downstream workflow outputs.

The model routing policy is also independent from live trading. Choosing a cheaper or stronger review model does not enable live order submission, change exchange credentials, raise risk caps, or promote a model to live trading.

## Prevention

- Pin model and effort explicitly for secret-bearing or merge-blocking AI gates.
- Keep AI Review Gate and auto-merge workflows separate.
- Keep `OPENAI_API_KEY` out of logs and pass it only to the Codex Action step.
- Never check out, build, run, install, or import PR head code in the AI Review Gate.
- Treat PR diffs and PR metadata as untrusted data.
- Use deterministic routing from changed files, labels, and PR metadata; do not ask the model to choose its own model.
- For GitHub PR files API, use `--slurp` with pagination or another safe aggregation method, then flatten before parsing.
- Inspect both `filename` and `previous_filename` for path-based policy.
- Treat trusted gate/policy docs as high-risk even when the PR is docs-only.
- Sanitize every PR-derived value before writing it to `GITHUB_OUTPUT`.
- Do not route required AI Gate decisions through nano models as the only judge.
- Do not silently fall back from a high-risk model to a cheaper model.

## Related Issues

- `docs/AI_REVIEW_GATE.md`
- `.github/workflows/ai-review-gate.yml`
- `.github/prompts/ai-review-gate.md`
- `docs/solutions/security-issues/ai-review-gate-secret-boundary-2026-05-18.md`
- `docs/solutions/security-issues/conditional-auto-merge-trust-boundary-2026-05-19.md`
