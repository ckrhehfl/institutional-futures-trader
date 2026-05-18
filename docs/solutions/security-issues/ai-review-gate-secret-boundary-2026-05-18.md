---
title: AI review gates must keep secrets in trusted workflow code
date: 2026-05-18
category: docs/solutions/security-issues
module: AI Review Gate
problem_type: security_issue
component: development_workflow
symptoms:
  - "A report-only AI review workflow needs an API key while reviewing untrusted PR diffs."
  - "Using pull_request would let PR-authored workflow YAML define the secret-bearing Codex invocation."
  - "A FAIL verdict should inform humans without blocking the workflow while the gate is still report-only."
root_cause: missing_workflow_step
resolution_type: workflow_improvement
severity: high
tags: [ai-review-gate, github-actions, pull-request-target, report-only, secret-boundary]
---

# AI review gates must keep secrets in trusted workflow code

## Problem

PR #11 added an AI Review Gate that uses Codex to inspect PR diffs and produce a report-only verdict. The original shape mixed a repository API key with workflow code that could be authored by the PR under review, which made the gate itself part of the untrusted surface.

## Symptoms

- The gate needed an API key to invoke Codex.
- The PR diff was untrusted input, but the workflow initially ran from the PR context.
- Review comments correctly flagged that protecting the prompt alone was insufficient when the workflow YAML could still be changed by the PR.
- Later review also flagged that `pull_request_target` changes the meaning of `github.ref`, so concurrency had to be scoped per PR.

## What Didn't Work

- Keeping `pull_request` while loading a trusted base-branch prompt did not protect the secret-bearing workflow step. The prompt was trusted, but the workflow definition was still PR-authored.
- Treating the AI verdict as a future required gate during this PR would have mixed report-only observation with merge policy.
- Posting PR comments or requesting `pull-requests: write` would have expanded the permission surface before the report format had proven stable.

## Solution

Use a trusted-workflow boundary for secret-bearing AI review:

- Run the AI review workflow with `pull_request_target` only when the repository owner explicitly accepts that event for this gate.
- Check out only the trusted base branch.
- Never check out, build, install, import, or execute PR head code.
- Collect the PR patch as text data, for example with `gh pr diff`, and store it as `.ai-review-gate/pr.diff`.
- Treat that diff as untrusted input to the model, not executable code.
- Load prompt and guidance from base-branch files.
- Pass the API key only to the Codex action step.
- Keep permissions at `contents: read` and `pull-requests: read`.
- Do not post PR comments and do not request write permissions.
- Output only a GitHub Actions job summary and a JSON artifact.
- Keep the workflow report-only: `PASS`, `FAIL`, and `NEEDS_OWNER_POLICY` are human signals, and the workflow still succeeds.
- Scope concurrency by PR number so one PR update does not cancel another PR's report-only run.

## Why This Works

The core separation is between trusted control plane and untrusted data plane. The workflow file, prompt, and repository guidance come from the trusted base branch. The PR contributes only a patch file that Codex reads as data. That keeps the repository API key out of PR-authored workflow code while still letting the model review the proposed change.

Report-only output also keeps this step separate from merge automation. Until the project has observed false positives, false negatives, and owner-policy conflicts across several PRs, the AI Review Gate should inform humans rather than block merges.

## Prevention

- For any workflow that uses repository secrets to inspect a PR, first identify whether the workflow definition itself is trusted.
- If a gate needs `pull_request_target`, document why it is allowed and explicitly forbid PR head checkout/build/run.
- Keep PR diffs as text artifacts, not as checked-out executable workspaces.
- Keep early AI gates report-only until their verdict quality and failure modes are observed.
- Avoid PR comments and write permissions unless a later owner decision explicitly needs them.
- When switching from `pull_request` to `pull_request_target`, review context values such as `github.ref` because they may now point at the base branch rather than the individual PR.

## Related Issues

- `docs/AI_REVIEW_GATE.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `docs/solutions/pr-review-loop-lessons.md`
