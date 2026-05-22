---
title: Closed PR events must disarm existing auto-merge requests
date: 2026-05-22
category: docs/solutions/workflow-issues
module: GitHub Actions auto-merge
problem_type: workflow_issue
component: development_workflow
severity: high
applies_when:
  - "GitHub auto-merge workflow가 PR의 auto-merge를 enable 또는 disable할 수 있는 경우"
  - "auto-merge가 이미 armed 된 뒤 PR이 eligible 상태에서 ineligible 상태로 바뀔 수 있는 경우"
  - "automation이 auto-merge를 enable한 뒤 사용자가 PR을 close하거나 cancel할 수 있는 경우"
  - "workflow eligibility logic이 open, closed, draft, retargeted 같은 lifecycle state에 의존하는 경우"
tags: [auto-merge, github-actions, lifecycle, closed-pr, fail-closed]
---

# Closed PR events must disarm existing auto-merge requests

## Context

PR #33은 사용자가 close했지만, 기존 GitHub auto-merge request가 armed 상태로 남아 있었다. 이후 checks가 통과하자 `github-actions[bot]`이 해당 PR을 `main`에 merge했다. 이는 live trading 문제가 아니라 auto-merge loop 안에서 발생한 `control-plane automation incident`였다.

PR #35는 `.github/workflows/auto-merge.yml`의 gap을 수정했다. 기존 workflow는 이미 `PR_STATE != open`을 `ineligible`로 처리했지만, `pull_request_target.types`에 `closed`가 없었다. 그래서 PR close event에서 workflow가 실행되지 않았고, ineligible path가 stale auto-merge request를 disable할 기회도 없었다.

## Guidance

`auto-merge` control loop는 forward-progress event와 cancellation event를 모두 trigger로 받아야 한다.

Forward-progress event에는 `opened`, `reopened`, `synchronize`, `ready_for_review`, `edited`, `labeled`, `unlabeled`가 포함된다. Cancellation 또는 disarming event에는 `closed`와, 이전 merge intent를 더 이상 신뢰하면 안 된다는 뜻의 future lifecycle event가 포함된다.

사용자가 PR을 close하는 행위는 auto-merge intent 취소로 취급한다. PR이 same-repository PR이고 auto-merge가 이미 enable되어 있었다면, close event에서 disable path가 실행되어야 한다.

## Why This Matters

Eligibility guard는 실제로 workflow를 trigger하는 상태 전이에 대해서만 보호 효과가 있다. `PR_STATE != open then ineligible` 같은 guard가 있어도, 그 상태로 바뀌는 event에서 workflow가 실행되지 않으면 충분하지 않다.

GitHub auto-merge는 stateful하다. 한 번 armed 되면 automation이 명시적으로 disarm하거나 GitHub가 merge를 거부하지 않는 한, 이후 metadata 변경 뒤에도 살아남을 수 있다. 따라서 event coverage는 단순 편의가 아니라 safety boundary의 일부다.

Durable rule은 다음과 같다.

1. PR을 ineligible로 만들 수 있는 event를 구독한다.
2. Job 내부에서 PR을 `ineligible`로 분류한다.
3. same-repository PR에 대해 disable path를 실행한다.
4. Disable failure를 조용히 넘기지 말고 visible failure로 만든다.
5. Cancellation event에서는 enable path가 실행되지 않게 막는다.

## Example

PR #35의 pattern은 다음과 같았다.

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

그 다음 enable step에 추가 guard를 둬서 `closed` event가 auto-merge를 다시 arm하지 못하게 한다.

```yaml
if: steps.eligibility.outputs.eligible == 'true' && github.event.action != 'closed'
```

Disable step은 먼저 GitHub auto-merge가 현재 enable되어 있는지 확인한다. 이렇게 하면 이미 disabled 된 closed PR과 실제 disable failure를 구분할 수 있다. Auto-merge가 enable되어 있는데 disable할 수 없다면 workflow는 fail closed하여 incident가 보이게 해야 한다.

## When To Apply

이 지침은 auto-merge, queued merge, deployment approval 또는 다른 control-plane automation처럼 persistent repository state를 arm하는 GitHub workflow를 설계하거나 리뷰할 때 적용한다.

리뷰할 때는 다음 질문을 던진다. "사용자가 intent를 cancel하거나 invalidate하면, workflow가 깨어나 armed state를 정리하는가?"

특히 auto-merge에서는 lifecycle edge case를 safety design의 일부로 포함한다.

- 사용자가 PR을 close함
- PR이 protected base branch 밖으로 retarget됨
- PR이 draft로 전환됨
- blocking label이 추가됨
- auto-merge enable 이후 high-risk file이 추가됨
- same-repository PR이 다른 이유로 `ineligible` 상태가 됨

## Related

- `.github/workflows/auto-merge.yml`
- `docs/AUTO_MERGE_POLICY.md`
- `docs/solutions/security-issues/conditional-auto-merge-trust-boundary-2026-05-19.md`
