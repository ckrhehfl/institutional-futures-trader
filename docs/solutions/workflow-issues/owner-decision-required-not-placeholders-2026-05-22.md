---
title: Owner decisions in committed docs must be explicit stop states, not placeholders
date: 2026-05-22
category: docs/solutions/workflow-issues
module: AI Operator Loop
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "Writing docs-only planning PRs that become repository source of truth"
  - "Leaving implementation prerequisites unresolved in committed documentation"
  - "AI Review Gate fails documentation because unresolved decisions look like placeholders"
  - "Distinguishing in-scope doc fixes from owner sign-off blockers"
tags: [documentation, owner-decision, ai-review-gate, review-triage, control-plane]
---

# Owner decisions in committed docs must be explicit stop states, not placeholders

## Context

PR #31 added `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md` as the implementation-before-contract for Discord-1a notification-only work. The PR intentionally did not implement a Discord bot, webhook sender, GitHub Actions workflow, OpenAI API automation, GitHub write path, or trading behavior.

AI Review Gate initially failed because the committed documentation used `확인 필요` for unresolved decisions such as dedup/idempotency ledger storage. That wording looked like an unfinished marker or ambiguous placeholder requirement, which violates the repository documentation rule that committed docs must not leave unfinished markers or ambiguous placeholder requirements.

The correct fix was not owner sign-off. The gate classification was `IN_SCOPE_DOC_OR_TEST_FIX`: replace placeholder wording with an explicit policy state. The PR changed those unresolved items to `OWNER_DECISION_REQUIRED`, explained that it is a stop state, and stated that the document does not approve implementation until a future owner-approved PR records concrete decisions.

## Guidance

Do not leave open-ended phrases such as `확인 필요`, `TBD`, `TODO`, `decide later`, or similar placeholders in committed planning docs.

If a decision is intentionally unresolved, write it as a policy state:

- `OWNER_DECISION_REQUIRED`
- not approved by this document
- implementation prohibited until a future owner-approved PR records the concrete decision

This turns ambiguity into an enforceable boundary. It also preserves the intended human role: the owner decides policy, risk, cost, permissions, and prohibitions; the document records that implementation must stop until that decision exists.

## Why This Matters

Docs-only planning PRs are still committed repository source of truth. Future agents may treat them as operating contracts. A placeholder like `확인 필요` can be interpreted as unfinished work, informal intent, or permission for the next agent to invent a decision.

An explicit stop state prevents that drift. It tells reviewers and agents:

1. the decision is known to be unresolved
2. the current PR does not approve it
3. implementation must stop there
4. owner approval is required in a later PR before proceeding

## Review Triage Rule

When AI Review Gate fails on a docs-only PR, inspect the gate classification before deciding how to respond.

- If the classification is `IN_SCOPE_DOC_OR_TEST_FIX`, fix the document within the current PR scope.
- If the classification is `OWNER_DECISION_REQUIRED`, stop and wait for owner sign-off.
- Do not assume every AI Review Gate failure on policy docs is an owner sign-off blocker.
- Do not keep editing a policy doc when the missing item is truly an owner decision.

PR #31 is the in-scope doc-fix case: the missing clarity was how unresolved decisions were represented, not whether the owner approved Discord-1a implementation.

## Example

Avoid this in committed docs:

```markdown
Dedup/idempotency ledger 저장 위치는 확인 필요입니다.
```

Prefer this:

```markdown
Dedup/idempotency ledger storage is `OWNER_DECISION_REQUIRED`.
This document does not approve a storage location. A future owner-approved
PR must record the concrete ledger storage decision before implementation starts.
```

## When To Apply

Use this guidance when:

- writing implementation-before-contract documents
- documenting future workflow, automation, webhook, permission, or control-plane work
- listing unresolved storage, hosting, permission, channel-access, or retention decisions
- responding to AI Review Gate documentation failures
- converting planning notes into committed repository docs

## Related

- `AGENTS.md`
- `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md`
- `docs/DISCORD_OPERATOR_BRIDGE.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `docs/solutions/workflow-issues/owner-policy-gates-for-control-plane-docs-2026-05-21.md`
