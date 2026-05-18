---
title: Conditional auto-merge must preserve repository trust boundaries
date: 2026-05-19
category: docs/solutions/security-issues
module: GitHub Actions auto-merge
problem_type: security_issue
component: development_workflow
symptoms:
  - "An auto-merge workflow needs write permissions while evaluating untrusted PR metadata."
  - "A PR can become ineligible after auto-merge was already enabled."
  - "High-risk files can be moved with rename metadata that is not visible in name-only diff output."
root_cause: missing_workflow_step
resolution_type: workflow_improvement
severity: high
tags: [auto-merge, github-actions, branch-protection, pull-request-target, trust-boundary]
---

# Conditional auto-merge must preserve repository trust boundaries

## Problem

PR #15 added conditional GitHub auto-merge for low-risk same-repository PRs. The durable risk is that an auto-merge workflow needs `contents: write` and `pull-requests: write`, so eligibility checks must be conservative and must never become a path around branch protection, AI Review Gate, or live trading gates.

## Symptoms

- Auto-merge required write permissions, but those permissions were only acceptable for enabling or disabling GitHub auto-merge.
- The workflow initially needed review to prove it did not call AI Review Gate, use `OPENAI_API_KEY`, post comments, or bypass branch protection.
- A PR retargeted away from `main` could previously skip the workflow before the disable path ran.
- A rename from a high-risk source path to a harmless-looking destination could be missed when only the current filename was inspected.

## What Didn't Work

- Treating auto-merge as part of AI Review Gate would have mixed the AI secret boundary with a write-permission merge workflow.
- Relying on branch protection by convention alone was not enough; the workflow also had to avoid `--admin` and use GitHub auto-merge rather than direct merge.
- Checking only PR head metadata or current filenames was too narrow. Eligibility can change after auto-merge is enabled, and rename metadata includes both current and previous paths.
- Skipping the job at the job-level when `base != main` prevented the workflow from disabling auto-merge for same-repository PRs retargeted away from `main`.

## Solution

Keep auto-merge as a separate, narrow workflow:

- Do not call AI Review Gate from the auto-merge workflow.
- Do not pass `OPENAI_API_KEY` or trading-related secrets to the auto-merge workflow.
- Do not use `actions/checkout`; inspect only GitHub PR metadata.
- Do not check out, build, run, install, or import PR head code.
- Exclude fork and external PRs from auto-merge.
- Use `gh pr merge --auto --squash --match-head-commit <HEAD_SHA>`.
- Never use `gh pr merge --admin`.
- Let branch protection and required checks decide whether GitHub can complete the merge.
- Re-evaluate eligibility on base branch edits.
- If a same-repository PR becomes ineligible, run `gh pr merge --disable-auto`.
- For renamed files, inspect both `.filename` and `.previous_filename` from the GitHub PR files API.
- Exclude workflow, prompt, policy, secret, credential, exchange adapter, and live-trading-boundary paths from auto-merge.

## Why This Works

The important boundary is that auto-merge is only a request to GitHub's existing merge machinery. It does not decide that a PR is safe to merge by itself, and it does not override CI, AI Review Gate, or branch protection.

Keeping AI Review Gate and auto-merge separate also keeps their permission models separate. AI Review Gate can remain read-only with secret-bearing AI invocation rules, while auto-merge can have narrowly scoped write permissions solely to enable or disable GitHub auto-merge.

Rechecking `base.ref` inside the eligibility step matters because a PR can change after the first evaluation. If the job is skipped when `base != main`, it cannot clean up previously enabled auto-merge. Treating non-main base branches as ineligible inside the job preserves the disable path for same-repository PRs.

Rename metadata matters for high-risk exclusions. `--name-only` style checks can see only the destination path, but a rename from `.github/workflows/ci.yml` to `docs/ci.txt` is still a workflow change. Checking `previous_filename` closes that gap.

## Prevention

- Keep write-permission automation separate from AI, secret-bearing, and live-trading workflows.
- For every auto-merge workflow, document the exact reason write permissions are allowed.
- Forbid `--admin`, direct merges, branch protection bypasses, and PR comments unless a later owner decision explicitly changes the policy.
- Subscribe to events that can change eligibility, including base branch edits, labels, draft state, and synchronize events.
- Put base branch checks inside eligibility logic when the workflow must also disable existing auto-merge.
- Use PR file metadata for path policy checks and include both current and previous filenames.
- Treat workflow/security/live-trading-boundary files as manual-merge-only even if all required checks pass.
- Keep auto-merge separate from live trading enablement, exchange credentials, risk cap increase, and model live promotion.

## Related Issues

- `docs/AUTO_MERGE_POLICY.md`
- `.github/workflows/auto-merge.yml`
- `docs/AI_REVIEW_GATE.md`
- `docs/solutions/security-issues/ai-review-gate-secret-boundary-2026-05-18.md`
