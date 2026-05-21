---
title: Control-plane policy docs need owner scope approval before fix loops
date: 2026-05-21
category: docs/solutions/workflow-issues
module: AI Operator Loop
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "Adding docs that define a new automation control plane or operator bridge"
  - "AI Review Gate returns NEEDS_OWNER_POLICY for a documentation-only PR"
  - "Codex review feedback is resolved but the merge gate still needs owner policy sign-off"
  - "Using Codex Cloud or app-based work on an existing PR branch"
tags: [owner-decision, ai-review-gate, codex-cloud, review-triage, control-plane]
---

# Control-plane policy docs need owner scope approval before fix loops

## Context

PR #28 added `docs/DISCORD_OPERATOR_BRIDGE.md` as the Discord-0 design document. The PR intentionally did not implement a Discord bot, GitHub Actions workflow, OpenAI API automation, GitHub App, permission expansion, source/test/runtime changes, or trading behavior.

Even though the diff was documentation-only, AI Review Gate classified the new Discord Operator Bridge as a new control-plane policy surface. The gate returned `NEEDS_OWNER_POLICY` until the owner explicitly confirmed that the document belonged in the PR scope.

That was not a bug to fix with repeated Codex edits. It was a policy decision. The correct loop was to stop, record the owner decision, and rerun the gate. After owner sign-off and in-scope review fixes, the PR merged through the existing conditional auto-merge path.

## Guidance

Treat documentation that defines new automation, operator commands, write paths, permission models, or merge-adjacent control planes as policy-bearing work.

Before trying repeated fixes, check whether the failing gate is asking for:

- a concrete in-scope document correction
- a missing owner policy decision
- allowed-files expansion
- roadmap or PR-scope approval
- permission or trust-boundary approval

If AI Review Gate returns `NEEDS_OWNER_POLICY`, classify the task as `STOPPED_POLICY` until an owner decision is recorded. Do not keep asking Codex to modify the same document hoping to make a policy blocker disappear.

For control-plane docs, make the owner-approved scope explicit in the PR body or owner comment:

- what document is approved
- whether the PR is design-only or implementation
- what rollout level is approved
- what permissions remain unapproved
- whether future write paths are intentionally only "confirmation needed"
- which files are allowed
- what the PR explicitly does not implement

## Why This Matters

AI Review Gate is doing useful work when it blocks a documentation-only PR that creates a new operating surface. A document can become source of truth for future automation even if it does not change code today.

Repeated Codex edits are the wrong response to an owner-policy blocker. They can create churn, widen the document, or accidentally convert unresolved decisions into implied approval. The safer pattern is:

1. stop the fix loop
2. identify the missing owner decision
3. record the decision in the PR context
4. only then make minimal in-scope doc corrections

This keeps humans in the intended role: policy, risk, prohibition, cost, and direction owner. It does not turn humans back into code-quality reviewers.

## Examples

PR #28 produced three distinct categories of work:

- `IN_SCOPE_DOC_OR_TEST_FIX`: align the stop condition so AI Review Gate `FAIL` stops after one occurrence.
- `IN_SCOPE_DOC_OR_TEST_FIX`: make `/pm status` output sanitized or redacted labels instead of raw labels.
- `OWNER_DECISION_REQUIRED`: decide whether Discord Operator Bridge belongs in the current roadmap/scope as a control-plane policy document.

Only the first two should be handled by document edits. The third requires owner sign-off.

When app-based Codex work pushes to an existing PR, verify the branch and remote before assuming the push succeeded:

```shell
git branch --show-current
git remote -v
git log --oneline -5
git diff --name-only HEAD~1..HEAD
git push origin HEAD:<existing-pr-branch>
```

If the push fails with a remote or authentication problem, classify it as `STOPPED_CODEX_FAILED` and report the exact failing command and error. Do not create a new branch or PR as a workaround for an existing PR branch push failure.

After pushing, confirm the PR commit list includes the expected commit. A local commit is not enough evidence that the GitHub PR was updated.

## Review Thread Resolution

PR #28 also confirmed that resolved Codex review threads can be marked resolved through GitHub GraphQL `resolveReviewThread`.

This is useful for cleanup after an in-scope fix has made a thread outdated or resolved. However, automatic review-thread resolution is itself a policy surface. Before adding it to a watcher or bot, decide:

- who may resolve threads
- whether only outdated threads may be auto-resolved
- whether owner-policy threads are excluded
- what audit trail is required
- what permissions the automation needs

Until that policy exists, treat thread resolution as a manual or explicitly owner-approved operation.

## When to Apply

Use this guidance when:

- a PR adds a design doc for a new automation or operator bridge
- a doc-only PR defines future commands, permissions, merge behavior, or fix loops
- AI Review Gate says `NEEDS_OWNER_POLICY`
- Codex review comments are fixed but branch protection still blocks on a policy gate
- Codex Cloud or app work reports that a local commit exists but the PR did not update

## Related

- `docs/DISCORD_OPERATOR_BRIDGE.md`
- `docs/AI_OPERATOR_LOOP.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `docs/AI_REVIEW_GATE.md`
- `docs/solutions/pr-review-loop-lessons.md`
- `docs/solutions/security-issues/ai-review-gate-secret-boundary-2026-05-18.md`
- `docs/solutions/security-issues/conditional-auto-merge-trust-boundary-2026-05-19.md`
