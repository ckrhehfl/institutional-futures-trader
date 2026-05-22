---
title: OMS state machine policy는 domain invariant와 정렬되어야 한다
date: 2026-05-23
category: docs/solutions/architecture-patterns
module: Core OMS
problem_type: architecture_pattern
component: service_object
severity: high
applies_when:
  - "order lifecycle 또는 State Machine helper를 추가할 때"
  - "safety-boundary transition policy를 export할 때"
  - "Codex Review finding이 in-scope bug와 owner-deferred policy를 함께 다룰 때"
  - "trusted roadmap의 current implementation step을 다음 단계로 넘길 때"
tags: [oms, state-machine, domain-invariants, review-triage, roadmap]
---

# OMS state machine policy는 domain invariant와 정렬되어야 한다

## Context

PR #50은 exchange-independent OMS State Machine v0 helper를 추가했다. 첫 버전은
`CREATED -> PENDING_RISK -> RISK_APPROVED/RISK_REJECTED`를 order status path로
다뤘지만, 기존 `Order` model은 concrete `Order` instance에서 `PENDING_RISK`와
`RISK_REJECTED` status를 거부한다.

따라서 새 State Machine은 기존 domain invariant와 맞지 않았다. v0에서 맞는
정책은 `PENDING_RISK`를 OMS order transition path 밖의 pre-order/pre-risk
state로 두고, `RISK_REJECTED`는 no-auto-forward stop state로 유지하며,
concrete order transition은 `CREATED -> RISK_APPROVED`에서 시작하는 것이다.

PR #50은 두 가지 workflow 교훈도 함께 드러냈다. Exported safety policy는
runtime에서 mutable하면 안 되며, implementation PR은 AI Review Gate가 scope를
판단할 수 있도록 trusted roadmap의 current step과 정렬되어야 한다.

## Guidance

State Machine helper는 고립된 table이 아니다. 실행 가능한 architecture contract이므로
merge 전에 기존 domain model invariant와 맞는지 확인해야 한다.

OMS/order lifecycle helper를 다룰 때는 다음을 확인한다.

- transition table을 승인하기 전에 기존 `Order`, `OrderIntent`, 관련 enum constraint를
  먼저 읽는다.
- domain model이 표현할 수 없는 transition target을 추가하지 않는다.
- Recovery policy가 아직 승인되지 않았다면 `UNKNOWN` 같은 uncertain state는 명시적인
  operator-review stop state로 유지한다.
- Recovery transition은 initial State Machine에 즉흥적으로 추가하지 않고 future
  reconciliation policy PR로 분리한다.
- Transition policy는 `MappingProxyType`과 `frozenset` value처럼 immutable data로
  노출해, 다른 module이 process-wide guard behavior를 바꾸지 못하게 한다.

Codex Review가 여러 finding을 보고하면, 코드를 바꾸기 전에 각 항목을
`docs/PR_REVIEW_PLAYBOOK.md` 기준으로 분류한다.

- `IN_SCOPE_BUG`: 실패 테스트를 먼저 추가하거나 갱신한 뒤 가장 작은 code fix를 적용한다.
- `OWNER_DECISION_REQUIRED`: severity label이 높다는 이유만으로 제안을 구현하지 않는다.
- Future recovery 또는 reconciliation semantics는 owner가 해당 policy surface를
  승인하지 않았다면 deferred 상태로 둔다.

## Why This Matters

Order State Machine은 safety boundary다. Domain model이 거부하는 전이를 허용하면
downstream code는 dead-end에 걸리거나 State Machine을 우회하는 방향을 배우게 된다.
두 경우 모두 runtime이 생기기 전에 OMS/Risk/ExecutionGateway boundary를 약화한다.

Exported transition table을 runtime에서 mutate할 수 있어도 비슷한 문제가 생긴다.
Process가 import 이후 accepted lifecycle policy를 조용히 바꿀 수 있고, tests가 더
이상 production behavior를 설명하지 못할 수 있다.

Roadmap alignment도 중요하다. AI Review Gate는 trusted docs를 source of truth로
본다. `docs/DEVELOPMENT_ROADMAP.md`가 여전히 current implementation step을 Risk
Engine Interface Only로 표시하면, owner가 PR conversation에서 OMS implementation을
승인했더라도 Gate는 `NEEDS_OWNER_POLICY`로 막을 수 있다.

## When to Apply

- `OrderStatus` transition policy를 추가하거나 바꿀 때
- 새 State Machine 또는 lifecycle validator를 도입할 때
- core module에서 policy table을 export할 때
- lifecycle semantics 관련 Codex Review comment를 처리할 때
- roadmap implementation step을 다음 단계로 넘길 때

## Examples

PR #50은 v0에서 다음 규칙을 고정했다.

```text
CREATED -> RISK_APPROVED
RISK_APPROVED -> ACCEPTED
ACCEPTED -> SUBMITTED
SUBMITTED -> PARTIALLY_FILLED / FILLED / CANCELED / REJECTED / EXPIRED / UNKNOWN
PARTIALLY_FILLED -> FILLED / CANCELED / EXPIRED / UNKNOWN
```

또한 v0에서 다음 전이는 금지로 고정했다.

```text
PENDING_RISK -> *
* -> PENDING_RISK
* -> RISK_REJECTED
UNKNOWN -> *
```

`UNKNOWN -> *` review는 의도적으로 구현하지 않았다. v0에서 `UNKNOWN`은
operator-review stop state다. Unknown outcome을 resolve하는 정책은 future
reconciliation policy에 속한다.

## Related

- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `src/trading_system/core/domain/models.py`
- `src/trading_system/core/domain/enums.py`
- `src/trading_system/core/oms/state_machine.py`
- `tests/core/oms/test_state_machine.py`
- `docs/solutions/pr-review-loop-lessons.md`
- `docs/solutions/workflow-issues/owner-policy-gates-for-control-plane-docs-2026-05-21.md`
