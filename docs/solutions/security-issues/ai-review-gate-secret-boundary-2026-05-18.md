---
title: AI review gates must keep secrets in trusted workflow code
date: 2026-05-18
last_updated: 2026-05-18
category: docs/solutions/security-issues
module: AI Review Gate
problem_type: security_issue
component: development_workflow
symptoms:
  - "A report-only AI review workflow needs an API key while reviewing untrusted PR diffs."
  - "Using pull_request would let PR-authored workflow YAML define the secret-bearing Codex invocation."
  - "A FAIL verdict should inform humans without blocking the workflow while the gate is still report-only."
  - "A required-check-ready gate can be bypassed if it accepts an internally inconsistent PASS report."
root_cause: missing_workflow_step
resolution_type: workflow_improvement
severity: high
tags: [ai-review-gate, github-actions, pull-request-target, required-check, secret-boundary]
---

# AI review gates must keep secrets in trusted workflow code

## Problem

PR #11 added an AI Review Gate that uses Codex to inspect PR diffs and produce a report-only verdict. The original shape mixed a repository API key with workflow code that could be authored by the PR under review, which made the gate itself part of the untrusted surface. PR #13 then promoted the gate to required-check-ready behavior, which added a second durable lesson: a merge-blocking AI gate must not accept a `PASS` verdict unless the full report is internally consistent.

## Symptoms

- The gate needed an API key to invoke Codex.
- The PR diff was untrusted input, but the workflow initially ran from the PR context.
- Review comments correctly flagged that protecting the prompt alone was insufficient when the workflow YAML could still be changed by the PR.
- Later review also flagged that `pull_request_target` changes the meaning of `github.ref`, so concurrency had to be scoped per PR.
- When the gate became required-check-ready, review flagged that `{"verdict": "PASS", "owner_decision_required": true}` or a `checks` entry set to `fail` could otherwise pass solely because the verdict string was `PASS`.

## What Didn't Work

- Keeping `pull_request` while loading a trusted base-branch prompt did not protect the secret-bearing workflow step. The prompt was trusted, but the workflow definition was still PR-authored.
- Treating the AI verdict as a future required gate during this PR would have mixed report-only observation with merge policy.
- Posting PR comments or requesting `pull-requests: write` would have expanded the permission surface before the report format had proven stable.
- Enforcing only `verdict == "PASS"` is too weak for a branch-protection gate because the report is model-generated and may contain contradictory fields.

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
- When promoting from report-only to required-check-ready, succeed only on a consistent passing report:
  - `verdict` is `PASS`
  - `owner_decision_required` is `false`
  - the expected `checks` keys are present
  - every `checks` value is `pass`
- Scope concurrency by PR number so one PR update does not cancel another PR's report-only run.

## Why This Works

The core separation is between trusted control plane and untrusted data plane. The workflow file, prompt, and repository guidance come from the trusted base branch. The PR contributes only a patch file that Codex reads as data. That keeps the repository API key out of PR-authored workflow code while still letting the model review the proposed change.

Report-only output also keeps this step separate from merge automation. After the project promotes the gate to required-check-ready behavior, the workflow still remains separate from auto-merge and live trading enablement. It simply converts inconsistent or negative AI reports into a failed check once the owner marks the workflow as required in branch protection.

A consistent PASS requirement matters because the model controls the JSON fields. If the workflow trusts only the `verdict` string, contradictory reports can turn unresolved policy or safety findings into a green check. Checking the full report shape keeps branch protection aligned with the gate's actual meaning.

## Prevention

- For any workflow that uses repository secrets to inspect a PR, first identify whether the workflow definition itself is trusted.
- If a gate needs `pull_request_target`, document why it is allowed and explicitly forbid PR head checkout/build/run.
- Keep PR diffs as text artifacts, not as checked-out executable workspaces.
- Keep early AI gates report-only until their verdict quality and failure modes are observed.
- Before making an AI gate required-check-ready, define the full consistency contract for `PASS`, not just the verdict enum.
- Treat missing, invalid, or internally inconsistent JSON as `NEEDS_OWNER_POLICY`.
- Avoid PR comments and write permissions unless a later owner decision explicitly needs them.
- When switching from `pull_request` to `pull_request_target`, review context values such as `github.ref` because they may now point at the base branch rather than the individual PR.

## Related Issues

- `docs/AI_REVIEW_GATE.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `docs/solutions/pr-review-loop-lessons.md`
