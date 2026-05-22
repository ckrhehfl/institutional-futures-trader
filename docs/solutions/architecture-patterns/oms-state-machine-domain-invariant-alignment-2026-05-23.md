---
title: OMS state machine policy must align with domain invariants
date: 2026-05-23
category: docs/solutions/architecture-patterns
module: Core OMS
problem_type: architecture_pattern
component: service_object
severity: high
applies_when:
  - "Adding an order lifecycle or state machine helper"
  - "Exporting safety-boundary transition policy"
  - "Handling Codex Review findings that mix in-scope bugs and owner-deferred policy"
  - "Advancing the current implementation step in the trusted roadmap"
tags: [oms, state-machine, domain-invariants, review-triage, roadmap]
---

# OMS state machine policy must align with domain invariants

## Context

PR #50 added the exchange-independent OMS State Machine v0 helper. The first version
treated `CREATED -> PENDING_RISK -> RISK_APPROVED/RISK_REJECTED` as the order status
path, but the existing `Order` model rejects `PENDING_RISK` and `RISK_REJECTED`
statuses for concrete `Order` instances.

That made the new state machine inconsistent with the existing domain invariant.
The correct v0 policy was to treat `PENDING_RISK` as pre-order/pre-risk state outside
the OMS order transition path, keep `RISK_REJECTED` as no-auto-forward stop state, and
start concrete order transitions at `CREATED -> RISK_APPROVED`.

PR #50 also exposed two workflow lessons: exported safety policy must not be mutable
at runtime, and implementation PRs must keep the trusted roadmap aligned with the
approved current step before AI Review Gate can treat the work as in scope.

## Guidance

State machine helpers are not isolated tables. They are executable architecture
contracts and must be checked against existing domain model invariants before merge.

For OMS/order lifecycle helpers:

- Read the existing `Order`, `OrderIntent`, and related enum constraints before
  approving a transition table.
- Do not introduce a transition target that the domain model cannot represent.
- Keep uncertain states such as `UNKNOWN` as explicit operator-review stop states
  when recovery policy is not yet approved.
- Put recovery transitions in a future reconciliation policy PR instead of adding
  them opportunistically to the initial state machine.
- Expose transition policy as immutable data, such as `MappingProxyType` with
  `frozenset` values, so another module cannot mutate guard behavior process-wide.

When Codex Review reports multiple findings, classify each item through
`docs/PR_REVIEW_PLAYBOOK.md` before changing code.

- `IN_SCOPE_BUG`: add or update a failing test first, then make the smallest code fix.
- `OWNER_DECISION_REQUIRED`: do not implement the suggestion just because it has a
  high severity label.
- Future recovery or reconciliation semantics should stay deferred when the owner has
  not approved that policy surface.

## Why This Matters

An order state machine is a safety boundary. If it allows transitions that the domain
model rejects, downstream code either dead-ends or learns to bypass the state machine.
Both outcomes weaken the OMS/Risk/ExecutionGateway boundary before runtime exists.

Runtime-mutating an exported transition table has a similar failure mode. The process
can silently change the accepted lifecycle policy after import, and tests may no
longer describe production behavior.

Roadmap alignment matters because AI Review Gate treats trusted docs as source of
truth. If `docs/DEVELOPMENT_ROADMAP.md` still says the current implementation step is
Risk Engine Interface Only, an OMS implementation can be correctly blocked as
`NEEDS_OWNER_POLICY` even when the owner approved the PR in conversation.

## When to Apply

- Adding or changing `OrderStatus` transition policy
- Introducing a new state machine or lifecycle validator
- Exporting policy tables from core modules
- Handling Codex Review comments on lifecycle semantics
- Moving from one roadmap implementation step to the next

## Examples

PR #50 settled these v0 rules:

```text
CREATED -> RISK_APPROVED
RISK_APPROVED -> ACCEPTED
ACCEPTED -> SUBMITTED
SUBMITTED -> PARTIALLY_FILLED / FILLED / CANCELED / REJECTED / EXPIRED / UNKNOWN
PARTIALLY_FILLED -> FILLED / CANCELED / EXPIRED / UNKNOWN
```

It also settled these v0 prohibitions:

```text
PENDING_RISK -> *
* -> PENDING_RISK
* -> RISK_REJECTED
UNKNOWN -> *
```

The `UNKNOWN -> *` review was intentionally not implemented. In v0, `UNKNOWN` is an
operator-review stop state. Resolving unknown outcomes belongs to a future
reconciliation policy.

## Related

- `docs/DEVELOPMENT_ROADMAP.md`
- `docs/PR_REVIEW_PLAYBOOK.md`
- `src/trading_system/core/domain/models.py`
- `src/trading_system/core/domain/enums.py`
- `src/trading_system/core/oms/state_machine.py`
- `tests/core/oms/test_state_machine.py`
- `docs/solutions/pr-review-loop-lessons.md`
- `docs/solutions/workflow-issues/owner-policy-gates-for-control-plane-docs-2026-05-21.md`
