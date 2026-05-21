---
title: 미정 owner decision은 placeholder가 아니라 명시적 stop state로 기록한다
date: 2026-05-22
category: docs/solutions/workflow-issues
module: AI Operator Loop
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "docs-only planning PR이 repository source of truth가 되는 경우"
  - "구현 전 prerequisite가 committed documentation 안에 미정으로 남는 경우"
  - "AI Review Gate가 미정 decision을 placeholder로 판단해 실패하는 경우"
  - "in-scope doc fix와 owner sign-off blocker를 구분해야 하는 경우"
tags: [documentation, owner-decision, ai-review-gate, review-triage, control-plane]
---

# 미정 owner decision은 placeholder가 아니라 명시적 stop state로 기록한다

## Context

PR #31은 Discord-1a notification-only 작업을 위한 implementation-before-contract 문서인 `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md`를 추가했다. 이 PR은 의도적으로 Discord bot, webhook sender, GitHub Actions workflow, OpenAI API automation, GitHub write path, trading behavior를 구현하지 않았다.

AI Review Gate는 처음에 실패했다. 이유는 committed documentation 안에서 dedup/idempotency ledger storage 같은 미정 decision을 `확인 필요`로 표현했기 때문이다. 이 표현은 unfinished marker 또는 ambiguous placeholder requirement처럼 보였고, committed docs에 unfinished marker나 ambiguous placeholder requirement를 남기지 말라는 repository Documentation Rules와 충돌했다.

올바른 수정은 owner sign-off를 추가하는 것이 아니었다. Gate classification은 `IN_SCOPE_DOC_OR_TEST_FIX`였다. 즉, placeholder wording을 명시적인 policy state로 바꾸는 문서 수정이 필요했다. PR #31은 미정 항목을 `OWNER_DECISION_REQUIRED`로 바꾸고, 그것이 stop state임을 설명했으며, future owner-approved PR이 concrete decision을 기록하기 전까지 implementation을 승인하지 않는다고 명시했다.

## Guidance

Committed planning docs에는 `확인 필요`, `TBD`, `TODO`, `decide later` 같은 open-ended placeholder를 남기지 않는다.

Decision이 의도적으로 미정이라면 policy state로 기록한다.

- `OWNER_DECISION_REQUIRED`
- 이 문서는 해당 결정을 승인하지 않음
- future owner-approved PR이 concrete decision을 기록하기 전까지 implementation prohibited

이 방식은 모호함을 enforceable boundary로 바꾼다. 또한 owner의 역할을 보존한다. Owner는 policy, risk, cost, permissions, prohibitions를 결정하고, 문서는 그 결정이 존재하기 전까지 implementation이 멈춰야 한다는 사실을 기록한다.

## Why This Matters

Docs-only planning PR도 merge되면 repository source of truth가 된다. Future agents는 이 문서를 operating contract로 취급할 수 있다. `확인 필요` 같은 placeholder는 unfinished work, informal intent, 또는 다음 agent가 decision을 임의로 만들어도 된다는 신호로 오해될 수 있다.

명시적인 stop state는 이런 drift를 막는다. Reviewers와 agents에게 다음 사실을 분명히 알려준다.

1. 해당 decision은 미정임이 이미 알려져 있다.
2. 현재 PR은 그 decision을 승인하지 않는다.
3. implementation은 그 지점에서 멈춰야 한다.
4. 진행하려면 later PR에서 owner approval이 필요하다.

## Review Triage Rule

AI Review Gate가 docs-only PR에서 실패하면, 대응하기 전에 gate classification을 먼저 확인한다.

- classification이 `IN_SCOPE_DOC_OR_TEST_FIX`이면 현재 PR scope 안에서 문서를 수정한다.
- classification이 `OWNER_DECISION_REQUIRED`이면 멈추고 owner sign-off를 기다린다.
- policy docs에서 AI Review Gate가 실패했다고 해서 모두 owner sign-off blocker라고 가정하지 않는다.
- 실제로 owner decision이 빠진 경우에는 policy doc을 계속 고치지 않는다.

PR #31은 in-scope doc-fix 사례다. 부족했던 것은 owner가 Discord-1a implementation을 승인했는지 여부가 아니라, unresolved decision을 어떤 정책 상태로 표현해야 하는지에 대한 clarity였다.

## Example

Committed docs에서 이런 표현은 피한다.

```markdown
Dedup/idempotency ledger 저장 위치는 확인 필요입니다.
```

대신 이렇게 쓴다.

```markdown
Dedup/idempotency ledger storage is `OWNER_DECISION_REQUIRED`.
This document does not approve a storage location. A future owner-approved
PR must record the concrete ledger storage decision before implementation starts.
```

위 예시의 `확인 필요`는 금지 패턴을 설명하기 위한 예시이며, 실제 미정 requirement로 남긴 것이 아니다.

## When To Apply

이 지침은 다음 상황에서 적용한다.

- implementation-before-contract 문서를 작성할 때
- future workflow, automation, webhook, permission, control-plane work를 문서화할 때
- storage, hosting, permission, channel-access, retention decision이 아직 승인되지 않았을 때
- AI Review Gate documentation failure에 대응할 때
- planning note를 committed repository docs로 바꿀 때

## Related

- `AGENTS.md`
- `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md`
- `docs/DISCORD_OPERATOR_BRIDGE.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `docs/solutions/workflow-issues/owner-policy-gates-for-control-plane-docs-2026-05-21.md`
