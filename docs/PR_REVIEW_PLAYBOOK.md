# PR Review Playbook

이 문서는 PR 리뷰 코멘트를 현재 PR 범위에 맞게 분류하고 처리하기 위한 기준입니다. PR 설명의 Scope, Non-goals, Allowed files / layers와 `AGENTS.md`를 함께 적용하며, 충돌하면 더 좁은 범위를 따릅니다.

## Review Comment Classification

- `IN_SCOPE_BUG`: 현재 PR scope 안에 있고 실제 동작, invariant, type, validation, secret, live/demo/paper boundary, exchange-independent core, regression test와 관련된 문제입니다.
- `IN_SCOPE_DOC_OR_TEST_FIX`: 현재 PR 목적을 더 명확하게 만드는 문서 모순, 불명확성, 또는 현재 PR의 regression test 보강입니다. 새 기능 구현은 포함하지 않습니다.
- `OUT_OF_SCOPE_FOLLOW_UP`: 지적은 의미 있지만 현재 PR 범위 밖입니다. adapter, REST/WebSocket, strategy, ML, trading engine, OMS, Risk Engine, live trading, event bus runtime, database/storage runtime, production deployment 요구가 여기에 해당합니다.
- `OPTIONAL_OR_STYLE`: 이름, 표현, 구조, readability 개선 정도이며 merge를 막는 실제 문제가 아닙니다.
- `OWNER_DECISION_REQUIRED`: 리뷰가 `AGENTS.md`, PR 설명, owner 판단과 충돌하거나 코드 수정으로 해결하면 PR 범위가 커지는 경우입니다.

## Handling Rules

- `IN_SCOPE_BUG`는 테스트 우선으로 수정합니다. 가능하면 실패 테스트를 먼저 추가하고 최소 구현으로 통과시킵니다.
- `IN_SCOPE_DOC_OR_TEST_FIX`는 현재 PR 범위 안에서만 수정합니다.
- `OUT_OF_SCOPE_FOLLOW_UP`은 다음 PR로 넘기고 현재 PR에서는 코드 변경하지 않습니다.
- `OPTIONAL_OR_STYLE`은 merge blocker가 아니면 보류하거나 follow-up으로 남깁니다.
- `OWNER_DECISION_REQUIRED`는 사람이 판단 댓글을 남기고, 판단 전에는 코드 변경하지 않습니다.
- P1/P2라도 현재 PR scope 밖이면 바로 수정하지 않습니다.
- allowed files 밖 변경이 필요하면 현재 PR에서 멈추고 owner 판단을 요청합니다.

## GitHub Thread Reply Templates

### Out Of Scope Follow-Up

```markdown
This is a useful follow-up, but it is outside this PR's Scope/Allowed files. This PR intentionally does not implement <area>. I am leaving this for a follow-up PR so this change stays focused.
```

### Owner Decision Required

```markdown
This conflicts with the current PR Scope/Non-goals or would expand the change beyond the allowed layer. Owner decision needed: should this PR expand scope, or should this become a follow-up?
```

### Code Implementation Requested In A Documentation PR

```markdown
This PR is documentation-only. Implementing this would require code/runtime changes outside the allowed files, so I am not changing code here. I can capture it as a follow-up implementation item.
```

### Optional Or Style Feedback Deferred

```markdown
This looks optional/style-level and does not block the current Scope. I am deferring it to avoid expanding the PR. It can be handled in a follow-up cleanup if desired.
```

## Stop Before Merge

Stop the merge when any of these are true:

- A P1/P2 actual bug inside the current PR scope remains unresolved.
- There are changes outside the PR's allowed files or layers.
- Validation failed or required verification was not run.
- A secret, API key, account id, wallet address, raw exchange credential, or `.env` content entered the diff.
- Live/demo/paper boundaries are blurred by the change.
- The PR requires owner decision and the decision has not been made.

Merge can proceed after human judgment when the only remaining comments are out-of-scope follow-ups, optional/style comments, or owner-accepted deferrals.

## Squash Merge Criteria

- Use squash merge when review response commits are numerous or noisy.
- Main should keep one meaningful commit for the PR's durable change.
- Preserve the PR description's Scope and Non-goals in the squash commit message when possible.

## Compound Learning Loop

At the end of each PR, answer:

- What mistake repeated in this PR?
- Was the mistake bug, scope, review, validation, architecture, or prompt related?
- Where should prevention live?
  - bug: test
  - scope: `AGENTS.md` or PR template
  - review judgment: `docs/PR_REVIEW_PLAYBOOK.md`
  - architecture: roadmap or architecture docs
  - long repeated prompt: custom skill candidate
  - validation gap: pre-commit, CI, or checklist
- Was prevention added now, or left as a follow-up?

Run `/ce-compound` after merge when the learning is durable. If `/ce-compound` is unavailable, write a manual compound note under `docs/solutions/`.

## Superpowers + Compound Engineering Workflow

- Before work starts, define Scope, Non-goals, and Allowed files / layers.
- After implementation, run Superpowers code review for implementation PRs before PR creation or before merge.
- When PR review arrives, classify each comment using this playbook before editing.
- After merge, run `/ce-compound` or write a manual compound note.
- Consider creating a custom skill only when the same long prompt or workflow repeats three or more times.
