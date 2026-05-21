---
title: Committed docs must use OWNER_DECISION_REQUIRED instead of placeholders
date: 2026-05-22
category: docs/solutions/workflow-issues
module: AI Operator Loop
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "docs-only planning PR이 repository source of truth가 되는 경우"
  - "committed documentation에 구현 전제 조건이 미정으로 남는 경우"
  - "AI Review Gate가 unresolved decision을 placeholder로 판단하는 경우"
  - "in-scope doc fix와 owner sign-off blocker를 구분해야 하는 경우"
tags: [documentation, owner-decision, ai-review-gate, review-triage, control-plane]
---

# Committed docs must use OWNER_DECISION_REQUIRED instead of placeholders

## Context

PR #31은 Discord-1a notification-only 작업의 구현 전 계약으로 `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md`를 추가했다. 이 PR은 의도적으로 Discord bot, webhook sender, GitHub Actions workflow, OpenAI API automation, GitHub write path, trading behavior를 구현하지 않았다.

처음 AI Review Gate는 committed documentation 안에 unresolved decision을 `확인 필요`처럼 적은 점을 이유로 실패했다. 예를 들어 dedup/idempotency ledger storage 같은 항목이 명확한 정책 상태가 아니라 unfinished marker 또는 ambiguous placeholder requirement처럼 보였다. 이는 committed documentation에 unfinished marker나 ambiguous placeholder requirement를 남기지 말라는 저장소 documentation rule과 충돌한다.

올바른 대응은 owner sign-off를 요청하는 것이 아니었다. Gate classification은 `IN_SCOPE_DOC_OR_TEST_FIX`였고, 필요한 수정은 placeholder wording을 명시적인 policy state로 바꾸는 것이었다. PR #31은 해당 항목들을 `OWNER_DECISION_REQUIRED`로 바꾸고, 이것이 `stop state`이며 future owner-approved PR이 concrete decision을 기록하기 전까지 구현을 승인하지 않는다고 설명했다.

## Guidance

Committed planning docs에는 `확인 필요`, `TBD`, `TODO`, `decide later`처럼 열린 표현을 남기지 않는다.

의도적으로 unresolved decision을 남겨야 한다면 policy state로 쓴다.

- `OWNER_DECISION_REQUIRED`
- 이 문서는 해당 결정을 승인하지 않음
- future owner-approved PR이 concrete decision을 기록하기 전까지 구현 금지

이렇게 쓰면 애매한 문구가 enforceable boundary로 바뀐다. 또한 사람의 역할도 유지된다. Owner는 policy, risk, cost, permissions, prohibitions를 결정하고, 문서는 그 결정이 존재하기 전까지 구현이 멈춰야 한다는 사실을 기록한다.

## Why This Matters

Docs-only planning PR도 merge되면 committed repository `source of truth`가 된다. Future agent는 그 문서를 운영 계약처럼 읽을 수 있다. `확인 필요` 같은 placeholder는 unfinished work, informal intent, 또는 다음 agent가 결정을 만들어도 된다는 허가처럼 해석될 수 있다.

명시적인 `stop state`는 이런 drift를 막는다. Reviewer와 agent에게 다음을 분명히 알려준다.

1. 해당 결정은 unresolved 상태임
2. 현재 PR은 그 결정을 승인하지 않음
3. 구현은 그 지점에서 멈춰야 함
4. 진행하려면 later PR에서 owner approval이 필요함

## Review Triage Rule

AI Review Gate가 docs-only PR에서 실패하면 대응하기 전에 gate classification을 먼저 확인한다.

- Classification이 `IN_SCOPE_DOC_OR_TEST_FIX`이면 현재 PR scope 안에서 문서를 수정한다.
- Classification이 `OWNER_DECISION_REQUIRED`이면 멈추고 owner sign-off를 기다린다.
- Policy docs에서 발생한 AI Review Gate failure가 항상 owner sign-off blocker라고 가정하지 않는다.
- 정말 owner decision이 필요한 항목이라면 policy doc을 계속 고쳐서 해결하려 하지 않는다.

PR #31은 in-scope doc-fix 사례였다. 부족했던 것은 owner가 Discord-1a implementation을 승인했는지가 아니라 unresolved decision을 어떻게 표현했는지였다.

## Example

Committed docs에서 피해야 할 표현:

```markdown
Dedup/idempotency ledger 저장 위치는 확인 필요입니다.
```

권장 표현:

```markdown
Dedup/idempotency ledger storage is `OWNER_DECISION_REQUIRED`.
This document does not approve a storage location. A future owner-approved
PR must record the concrete ledger storage decision before implementation starts.
```

## When To Apply

이 지침은 다음 상황에 적용한다.

- implementation-before-contract 문서를 작성할 때
- future workflow, automation, webhook, permission, control-plane 작업을 문서화할 때
- unresolved storage, hosting, permission, channel-access, retention decision을 나열할 때
- AI Review Gate documentation failure에 대응할 때
- planning note를 committed repository docs로 승격할 때

## Related

- `AGENTS.md`
- `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md`
- `docs/DISCORD_OPERATOR_BRIDGE.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `docs/solutions/workflow-issues/owner-policy-gates-for-control-plane-docs-2026-05-21.md`
