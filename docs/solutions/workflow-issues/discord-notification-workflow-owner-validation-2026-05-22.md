---
title: Discord notification workflow는 owner sign-off와 default-branch dry-run 검증이 필요하다
date: 2026-05-22
category: docs/solutions/workflow-issues
module: Discord-1a Notification
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "GitHub Actions workflow를 .github/workflows/** 아래에 추가하거나 수정하는 경우"
  - "redacted status를 GitHub 밖으로 보내는 read-only notification automation을 구현하는 경우"
  - "workflow implementation PR에서 AI Review Gate가 NEEDS_OWNER_POLICY를 반환하는 경우"
  - "merge 이후 default branch에서 workflow_dispatch 동작을 검증하는 경우"
tags: [discord, github-actions, owner-decision, ai-review-gate, workflow-dispatch]
---

# Discord notification workflow는 owner sign-off와 default-branch dry-run 검증이 필요하다

## 배경

PR #45는 첫 Discord-1a notification-only workflow인 `.github/workflows/discord-1a-notification.yml`을 추가했다. 구현 범위는 의도적으로 좁았다. GitHub Actions-only, read-only, notification-only였고 checkout, dependency install, PR head code execution, GitHub write path, Codex automation, persistent storage, raw PR text 또는 Codex output의 Discord 전송을 모두 제외했다.

owner-approved boundary docs가 이미 있어도 AI Review Gate는 `NEEDS_OWNER_POLICY`를 반환했다. `.github/workflows/**` 아래에 새 workflow를 추가하는 것은 scope-sensitive이자 high-risk automation surface이기 때문이다. 올바른 대응은 추가 코드 수정이 아니었다. PR conversation에 owner sign-off를 남기고 AI Review Gate를 rerun하는 것이 맞았다.

checks가 통과한 뒤에도 이 PR은 high-risk workflow automation이었다. 따라서 branch protection checks가 green이어도 conditional auto-merge가 항상 올바른 완료 경로는 아니다. 이런 workflow PR에서는 GitHub UI를 통한 owner-controlled manual merge가 정상 경로일 수 있다.

## 지침

`.github/workflows/**` 아래의 새 workflow 또는 수정된 workflow는 read-only라 해도 policy-bearing automation change로 취급한다.

Discord notification workflow에서는 대응 loop를 명확히 분리한다.

1. PR이 owner-approved boundary와 일치하는지 확인한다.
2. AI Review Gate가 `NEEDS_OWNER_POLICY`를 반환하면 fix loop를 멈춘다.
3. PR conversation에 owner sign-off를 기록한다.
4. AI Review Gate를 rerun한다.
5. checks가 통과했지만 PR이 high-risk workflow automation이면, auto-merge가 의도적으로 제외된 경우 owner-controlled manual merge를 사용한다.
6. merge 후 default branch에서 `workflow_dispatch`로 workflow를 검증한다.

default-branch validation이 중요한 이유는 GitHub Actions workflow가 merge 이후 default branch에서 운영 경로가 되기 때문이다. PR branch에 workflow file이 있어도, manual dispatch와 notification behavior의 owner validation은 merge 이후에 수행해야 한다.

검증은 dry-run부터 시작한다.

```text
workflow_dispatch
send_discord=false
```

이 경로는 redacted job summary만 남기고 Discord webhook secret을 요구하지 않아야 한다. 이후 owner가 `DISCORD_1A_WEBHOOK_URL`을 설정하면 다음 smoke test에서 `send_discord=true`를 사용할 수 있으며, redacted message를 최대 1개만 보내야 한다.

## 중요한 이유

read-only notification automation이라도 repository state를 다른 시스템으로 투영한다. Discord는 source of truth가 아니다. Discord는 GitHub PR, check, artifact state의 redacted/read-only projection이다. workflow는 무엇이든 보내기 전에 GitHub source-of-truth data를 재검증하고 unsafe path를 suppress할 수 있어야 한다.

owner-policy stop은 이 지점에서 유용하다. 새 control-plane workflow가 코드상 안전해 보인다는 이유만으로 승인된 것처럼 취급되는 일을 막는다. owner는 automation surface, permission boundary, trigger model, post-merge validation path를 명시적으로 승인해야 한다.

default-branch dry-run은 implementation correctness와 operational readiness를 분리한다. merge는 workflow file이 review와 branch protection을 통과했음을 의미한다. `workflow_dispatch` dry-run은 default-branch workflow가 raw PR text, secrets, Codex output을 노출하지 않고 실행될 수 있음을 확인한다.

## 적용 시점

이 지침은 다음 상황에서 적용한다.

- Discord, Slack, email 또는 다른 external channel로 notification workflow를 추가할 때
- workflow trigger 또는 permission boundary를 바꿀 때
- PR/check state를 관찰하는 `workflow_run` automation을 추가할 때
- AI Review Gate가 workflow PR을 `NEEDS_OWNER_POLICY`로 분류할 때
- read-only workflow가 repository secret에 의존하지만 dry-run validation에서는 그 secret이 필요하지 않아야 할 때

## 예시

안전한 first implementation은 workflow를 self-contained로 유지하고 unsafe path를 suppress한다.

```yaml
permissions:
  contents: read
  actions: read
  checks: read
  pull-requests: read
```

workflow는 다음을 사용하지 않는다.

```yaml
- uses: actions/checkout@v4
```

dry-run path는 webhook secret이 없어도 유용해야 한다.

```text
send_discord=false -> job summary only
missing webhook secret -> suppress Discord send
```

`workflow_run` notification에서는 GitHub source-of-truth metadata를 읽고, 다음 상황에서는 send가 아니라 suppress해야 한다.

- source workflow가 allowlist에 없을 때
- event에 PR number가 없을 때
- PR이 fork 또는 external repository에서 온 경우
- PR base가 `main`이 아닌 경우
- event head SHA가 더 이상 PR head SHA와 일치하지 않는 경우
- payload가 raw PR title, body, labels, diff, comments, review text, Codex output을 요구하는 경우

## 재발 방지

- `.github/workflows/**` 변경은 read-only workflow라도 owner-sign-off-gated로 유지한다.
- `NEEDS_OWNER_POLICY`에 반복 implementation edit로 대응하지 않는다.
- 이후 owner decision이 boundary를 명시적으로 바꾸기 전까지 notification workflow는 read-only로 유지한다.
- Discord payload를 위해 raw AI Review Gate artifact를 다운로드하거나 신뢰하지 않는다.
- merge-time behavior는 default branch에서 `workflow_dispatch`로 검증한다.
- 실제 webhook send를 테스트하기 전에 `send_discord=false`로 시작한다.
- logs, job summary, artifacts, Discord payload가 secrets, raw PR text, raw review text, raw Codex output, account data, wallet data, trading data를 노출하지 않는지 확인한다.
- `DISCORD_1A_WEBHOOK_URL` 누락은 failed implementation이 아니라 suppression path로 취급한다.

## 관련 문서

- `.github/workflows/discord-1a-notification.yml`
- `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md`
- `docs/DISCORD_1A_OWNER_DECISIONS.md`
- `docs/DISCORD_OPERATOR_BRIDGE.md`
- `docs/AUTOMATION_STATUS.md`
- `docs/solutions/workflow-issues/owner-policy-gates-for-control-plane-docs-2026-05-21.md`
- `docs/solutions/workflow-issues/github-actions-artifact-path-verification-2026-05-21.md`
- `docs/solutions/security-issues/conditional-auto-merge-trust-boundary-2026-05-19.md`
