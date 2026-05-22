---
title: Closed PR events must disarm existing auto-merge requests
date: 2026-05-22
category: docs/solutions/workflow-issues
module: GitHub Actions auto-merge
problem_type: workflow_issue
component: development_workflow
severity: high
applies_when:
  - "A GitHub auto-merge workflow can enable or disable auto-merge for PRs."
  - "A PR can move from eligible to ineligible after auto-merge has already been armed."
  - "A user can close or otherwise cancel a PR after automation has enabled auto-merge."
  - "Workflow eligibility logic depends on lifecycle state such as open, closed, draft, or retargeted."
tags: [auto-merge, github-actions, lifecycle, closed-pr, fail-closed]
---

# Closed PR events must disarm existing auto-merge requests

## Context

PR #33 was closed by the user, but an existing GitHub auto-merge request remained armed. After checks later passed, `github-actions[bot]` merged the PR into `main`. This was not a live trading issue. It was a control-plane automation incident in the auto-merge loop.

PR #35 fixed the gap in `.github/workflows/auto-merge.yml`. The workflow already treated `PR_STATE != open` as ineligible, but `pull_request_target.types` did not include `closed`. Because the workflow never ran on the close event, the ineligible path never had a chance to disable the stale auto-merge request.

## Guidance

Auto-merge control loops must subscribe to both forward-progress events and cancellation events.

Forward-progress events include `opened`, `reopened`, `synchronize`, `ready_for_review`, `edited`, `labeled`, and `unlabeled`. Cancellation or disarming events include `closed` and any future lifecycle event that means prior merge intent should no longer be trusted.

Treat a user closing a PR as cancellation of auto-merge intent. If the PR is same-repository and auto-merge was already enabled, the close event must run a disable path.

## Why This Matters

An eligibility guard only protects states that actually trigger the workflow. A line such as `if PR_STATE != open then ineligible` is not enough when the workflow does not run on the transition into that state.

GitHub auto-merge is stateful. Once armed, it can survive later metadata changes unless automation explicitly disarms it or GitHub rejects the merge. That means event coverage is part of the safety boundary, not just a convenience detail.

The durable rule is:

1. subscribe to the event that can make a PR ineligible
2. classify the PR as ineligible inside the job
3. run the disable path for same-repository PRs
4. make disable failure visible instead of silently continuing
5. prevent the enable path from running on cancellation events

## Example

The PR #35 pattern was:

```yaml
on:
  pull_request_target:
    types:
      - opened
      - reopened
      - synchronize
      - ready_for_review
      - edited
      - labeled
      - unlabeled
      - closed
```

Then the enable step is additionally guarded so `closed` cannot re-arm auto-merge:

```yaml
if: steps.eligibility.outputs.eligible == 'true' && github.event.action != 'closed'
```

The disable step first checks whether GitHub auto-merge is currently enabled. This distinguishes an already-disabled closed PR from a real disable failure. If auto-merge is enabled but cannot be disabled, the workflow fails closed so the incident is visible.

## When To Apply

Use this guidance when designing or reviewing any GitHub workflow that arms a persistent repository state, including auto-merge, queued merge, deployment approval, or other control-plane automation.

Ask this review question: "If a user cancels or invalidates the intent, does the workflow wake up and clean up the armed state?"

For auto-merge specifically, include lifecycle edge cases in the safety design:

- PR closed by the user
- PR retargeted away from the protected base branch
- PR converted to draft
- blocking label added
- high-risk file introduced after auto-merge was enabled
- same-repository PR becomes otherwise ineligible

## Related

- `.github/workflows/auto-merge.yml`
- `docs/AUTO_MERGE_POLICY.md`
- `docs/solutions/security-issues/conditional-auto-merge-trust-boundary-2026-05-19.md`
