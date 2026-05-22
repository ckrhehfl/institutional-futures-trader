# Discord-1a Owner Decisions

이 문서는 Discord-1a notification-only 구현 전에 owner가 결정해야 하는 항목을 고정하는 decision register입니다. 이 문서는 Discord-1a implementation을 승인하지 않습니다.

## Purpose

Discord-1a는 GitHub 상태를 Discord로 보내는 incoming webhook notification-only 단계로 설계되어 있습니다. 구현 전에 webhook storage, channel access, hosting, read identity, audit log, idempotency, rate limit, failure handling 같은 owner decision이 먼저 정리되어야 합니다.

이 문서의 목적은 Codex가 미정 정책을 임의로 선택하지 못하게 하고, 구현 전 stop state를 명확히 남기는 것입니다.

## This Document Does Not Approve Implementation

이 문서는 구현 승인 문서가 아닙니다.

- Discord webhook sender를 구현하지 않습니다.
- Discord bot, slash command, `/pm start`, `/pm status`, `/pm summary`를 구현하지 않습니다.
- GitHub Issue 생성, GitHub comment 작성, `@codex fix`, review-thread resolve, workflow rerun, auto-merge control, direct merge를 구현하지 않습니다.
- GitHub App, OpenAI API coding bot, GitHub write permission을 추가하지 않습니다.
- trading runtime, OMS, Risk implementation, BingX, strategy, ML, live trading을 구현하지 않습니다.
- live trading, exchange credentials, risk cap increase, model live promotion과 연결하지 않습니다.

이 문서의 모든 required owner decision은 승인 전 `OWNER_DECISION_REQUIRED` 상태입니다.

## Source-of-truth Boundary

Discord는 source of truth가 아닙니다. Discord는 GitHub 원본 상태를 사람이 빠르게 읽을 수 있도록 줄인 redacted/read-only projection입니다.

Discord-1a future implementation은 다음 GitHub source-of-truth input을 기준으로만 상태를 판단해야 합니다.

- PR metadata
- PR state
- base branch
- head branch
- remote head SHA
- PR commit list
- changed files
- check runs
- AI Review Gate status and artifact
- post-merge lesson capture status and artifact

Codex response, Discord message, GitHub UI summary만으로 다음 action을 진행하지 않습니다. Discord message는 approval signal이 아니며, `MERGE_ELIGIBLE`도 merge 승인 신호가 아닙니다.

## Decision Status Model

Decision status는 다음 값만 사용합니다.

| Status | Meaning |
| --- | --- |
| `OWNER_DECISION_REQUIRED` | owner decision이 없으므로 implementation이 금지된 상태입니다. |
| `APPROVED_BY_OWNER` | owner가 명시적으로 승인한 상태입니다. |
| `REJECTED_BY_OWNER` | owner가 명시적으로 거부한 상태입니다. 이 문서에서는 사용하지 않습니다. |

이 문서의 v1 update는 일부 최소 정책만 `APPROVED_BY_OWNER`로 기록합니다. 승인되지 않은 decision은 계속 `OWNER_DECISION_REQUIRED`, `Not approved`, `Implementation prohibited` 상태입니다.

## Decision Record Format

각 owner decision은 다음 형식을 따릅니다.

- Decision ID
- Question
- Current status: `OWNER_DECISION_REQUIRED`
- Allowed options
- Recommended option, if any
- Approved decision: `Not approved`
- Default until approved: `Implementation prohibited`
- Implementation impact
- Stop condition
- Evidence required before implementation

`Recommended option`은 구현 승인이나 owner approval이 아닙니다. `Approved decision`이 `Not approved`인 동안 구현은 금지됩니다.

## Required Owner Decisions

| Decision ID | Question | Current status | Allowed options | Recommended option, if any | Approved decision | Default until approved | Implementation impact | Stop condition | Evidence required before implementation |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1A-001 | Discord webhook URL storage / rotation을 어디에 두고 어떻게 회전할 것인가? | `APPROVED_BY_OWNER` | GitHub Actions repository secret | GitHub Actions repository secret | GitHub Actions repository secret에 저장합니다. Rotation은 owner가 수동으로 수행합니다. Secret 값은 로그, artifact, Discord message에 출력하지 않습니다. | `Implementation prohibited` for any other storage or rotation model | secret storage와 rotation process를 결정합니다. | secret value 출력 또는 다른 storage가 필요하면 구현 금지 | approved storage path, manual rotation owner, no-output validation |
| D1A-002 | Discord channel access scope를 어떻게 제한할 것인가? | `APPROVED_BY_OWNER` | private ops/status channel only | private ops/status channel only | private ops/status channel만 사용합니다. public channel, trading signal channel, customer-facing channel에는 전송하지 않습니다. | `Implementation prohibited` for any other channel type | 누가 notification을 볼 수 있는지 결정합니다. | private ops/status channel 밖 전송이 필요하면 구현 금지 | approved channel category and access boundary |
| D1A-003 | hosting model은 무엇인가? | `APPROVED_BY_OWNER` | GitHub Actions only | GitHub Actions only | Discord-1a는 GitHub Actions only로 제한합니다. external server, Discord bot process, GitHub App, OpenAI API coding bot은 사용하지 않습니다. | `Implementation prohibited` for any other hosting model | runtime location, secret exposure, audit path를 결정합니다. | external server, bot process, GitHub App, OpenAI API coding bot이 필요하면 구현 금지 | GitHub Actions-only implementation plan |
| D1A-004 | GitHub Actions 기반인지 external hosting 기반인지 어떻게 선택할 것인가? | `APPROVED_BY_OWNER` | GitHub Actions only | GitHub Actions only | Discord-1a v1은 GitHub Actions 기반입니다. external hosting은 승인하지 않습니다. | `Implementation prohibited` for external hosting | implementation file set과 permission model을 결정합니다. | external hosting이 필요하면 구현 금지 | GitHub Actions syntax and allowed files review |
| D1A-005 | GitHub read identity / permission boundary는 무엇인가? | `APPROVED_BY_OWNER` | minimum read-only GitHub Actions permissions | minimum read-only GitHub Actions permissions | GitHub Actions의 minimum read-only permissions만 사용합니다. `contents: write`, `pull-requests: write`, `issues: write`, `checks: write`, `actions: write` 등 write permission은 금지합니다. 정확한 permission key는 future implementation PR에서 GitHub Actions syntax 기준으로 재확인합니다. | `Implementation prohibited` if write permission is needed | GitHub API read scope를 결정합니다. | write permission이 필요하면 구현 금지 | permission list proving no write access |
| D1A-006 | audit log storage는 어디인가? | `OWNER_DECISION_REQUIRED` | GitHub Actions artifact, external log store, no persistent audit log for v1 | no persistent audit log for v1 | `Not approved` | `Implementation prohibited` | notification history와 incident review 가능성을 결정합니다. | long-term audit log storage가 필요하면 구현 금지 | log location, retention policy, redaction guarantee |
| D1A-007 | idempotency key / dedup ledger storage는 어디인가? | `OWNER_DECISION_REQUIRED` | GitHub Actions artifact, external storage, stateless per-run dedup only | stateless per-run dedup only | `Not approved` | `Implementation prohibited` | duplicate notification 방지 수준을 결정합니다. | persistent dedup ledger가 필요하면 구현 금지 | key format, storage path, retention policy |
| D1A-008 | raw event retention policy 세부 기간은 무엇인가? | `OWNER_DECISION_REQUIRED` | no raw event retention, redacted metadata only, owner-approved temporary retention | no raw event retention | `Not approved` | `Implementation prohibited` | PR body, raw labels, raw comments, raw diff 저장 여부와 기간을 결정합니다. | raw event retention이 필요하면 구현 금지 | retention policy proving raw sensitive text is not stored |
| D1A-009 | redaction failure policy는 무엇인가? | `APPROVED_BY_OWNER` | fail closed | fail closed | redaction이 실패하거나 확신할 수 없으면 fail closed하고 Discord 전송을 하지 않습니다. | `Implementation prohibited` for any send-on-uncertain-redaction behavior | redaction 실패 시 Discord 출력 여부를 결정합니다. | uncertain redaction 상태에서 전송이 필요하면 구현 금지 | redaction test cases and failure behavior |
| D1A-010 | stale-state control policy는 무엇인가? | `APPROVED_BY_OWNER` | revalidate before send; suppress on mismatch | revalidate before send; suppress on mismatch | Discord 전송 직전에 GitHub source-of-truth를 재확인합니다. PR head SHA, PR state, relevant check state가 기대값과 다르면 전송하지 않습니다. | `Implementation prohibited` for stale-state send behavior | GitHub source states가 불일치할 때 동작을 결정합니다. | stale state에서 전송 또는 action이 필요하면 구현 금지 | revalidation order and stale-state examples |
| D1A-011 | rate limits의 정확한 수치는 무엇인가? | `OWNER_DECISION_REQUIRED` | per-PR cap, per-hour cap, per-day cap, backoff on Discord 429 | per-hour and per-day cap | `Not approved` | `Implementation prohibited` | spam과 API pressure를 제한합니다. | numeric cap 없이 구현해야 하면 구현 금지 | numeric caps and backoff behavior |
| D1A-012 | failure notification policy의 세부 fallback은 무엇인가? | `OWNER_DECISION_REQUIRED` | suppress repeated failures, send redacted failure summary, owner-only escalation | redacted failure summary with repetition cap | `Not approved` | `Implementation prohibited` | webhook/API 실패 시 알림 방식을 결정합니다. | failure loop 가능성이 있으면 구현 금지 | failure classes, retry count, suppression rules |
| D1A-013 | fork/external PR notification policy는 무엇인가? | `APPROVED_BY_OWNER` | exclude fork/external PRs | exclude fork/external PRs | Discord-1a notification path에서도 fork/external PR은 제외합니다. | `Implementation prohibited` for fork/external PR notification path | untrusted external PR 상태를 Discord에 노출할지 결정합니다. | fork/external PR notification이 필요하면 구현 금지 | same-repo verification logic |
| D1A-014 | daily Codex request cap은 무엇인가? | `APPROVED_BY_OWNER` | zero automated Codex requests | zero automated Codex requests | Discord-1a의 automatic Codex request cap은 0입니다. Discord-1a는 Codex를 자동 호출하지 않습니다. | `Implementation prohibited` for automated Codex calls | Discord-1a가 Codex request를 유발하지 않도록 제한합니다. | automated Codex request가 필요하면 구현 금지 | enforcement showing no Codex call path |
| D1A-015 | Codex Review automation policy는 무엇인가? | `APPROVED_BY_OWNER` | no automation | no automation | Discord-1a는 Codex Review를 자동 호출하지 않습니다. Codex Review는 계속 advisory/manual 상태입니다. | `Implementation prohibited` for Codex Review automation | Codex Review를 notification path에 연결할지 결정합니다. | Codex Review automation이 필요하면 구현 금지 | no Codex Review call path |
| D1A-016 | automatic `@codex fix`를 허용할 것인가? | `APPROVED_BY_OWNER` | prohibited | prohibited | `Not approved`. Discord-1a에서 자동 `@codex fix`는 금지합니다. | `Implementation prohibited` for automatic fix flow | 자동 수정 loop 여부를 결정합니다. | automatic fix request가 필요하면 구현 금지 | no `@codex fix` call path |
| D1A-017 | review-thread resolve 자동화를 허용할 것인가? | `APPROVED_BY_OWNER` | prohibited | prohibited | `Not approved`. Discord-1a에서 review-thread resolve 자동화는 금지합니다. | `Implementation prohibited` for review-thread resolve automation | GitHub conversation resolution 권한 확장을 결정합니다. | automated resolve가 필요하면 구현 금지 | no resolveReviewThread call path |
| D1A-018 | post-merge lesson-loop prevention policy는 무엇인가? | `APPROVED_BY_OWNER` | no habitual merged-PR `@codex review`; separate post-merge lesson flow | no habitual merged-PR `@codex review`; separate post-merge lesson flow | merged PR에 습관적으로 `@codex review`를 호출하지 않습니다. post-merge lesson capture와 future lesson PR은 별도 flow로 유지합니다. | `Implementation prohibited` for automatic lesson-loop expansion | post-merge follow-up recursion 방지 수준을 결정합니다. | automatic post-merge review loop가 필요하면 구현 금지 | separate lesson flow and loop prevention statement |
| D1A-019 | Discord-1a implementation PR allowed files는 무엇인가? | `OWNER_DECISION_REQUIRED` | docs-only, single workflow, split PR sequence | split PR sequence after owner approval | `Not approved` | `Implementation prohibited` | future implementation blast radius를 결정합니다. | allowed files가 승인되지 않으면 구현 금지 | approved file list and non-goals |
| D1A-020 | owner sign-off approvers 확장 기준은 무엇인가? | `OWNER_DECISION_REQUIRED` | repository owner only, named maintainers, owner plus backup approver | repository owner only until expanded | `Not approved` | `Implementation prohibited` | policy approval authority를 결정합니다. | approver list가 승인되지 않으면 구현 금지 | approver list and sign-off format |
| D1A-021 | health check / recovery playbook 세부 절차는 무엇인가? | `OWNER_DECISION_REQUIRED` | manual recovery only, notification-only health check, future automated recovery | manual recovery only | `Not approved` | `Implementation prohibited` | 장애 감지와 복구 자동화 범위를 결정합니다. | automated recovery가 필요하면 구현 금지 | recovery steps and no-write guarantee |
| D1A-022 | future workflow trigger matrix는 무엇인가? | `OWNER_DECISION_REQUIRED` | pull_request_target read-only events, workflow_dispatch, scheduled polling, no workflow in v1 | no workflow in v1 until implementation scope is approved | `Not approved` | `Implementation prohibited` | 어떤 GitHub event에서 notification을 만들지 결정합니다. | trigger matrix가 승인되지 않으면 workflow 구현 금지 | approved trigger list and event safety analysis |
| D1A-023 | future Discord message schema는 무엇인가? | `OWNER_DECISION_REQUIRED` | compact status summary, redacted state transition, owner-action summary | compact redacted status summary | `Not approved` | `Implementation prohibited` | Discord에 표시할 field와 redaction boundary를 결정합니다. | schema가 승인되지 않으면 message sender 구현 금지 | approved field list and redaction examples |

## Not Approved Defaults

다음 default는 owner approval 전 항상 적용됩니다.

- Discord-1a implementation: `Implementation prohibited`
- Discord webhook sender: `Implementation prohibited`
- Discord bot and slash commands: `Implementation prohibited`
- GitHub write permission: `Implementation prohibited`
- `@codex fix` automation: `Implementation prohibited`
- review-thread resolve automation: `Implementation prohibited`
- workflow rerun automation: `Implementation prohibited`
- auto-merge control from Discord: `Implementation prohibited`
- direct merge from Discord or PM orchestrator: `Implementation prohibited`
- OpenAI API coding bot: `Implementation prohibited`
- live trading, exchange credentials, risk cap increase, model live promotion: `Implementation prohibited`

## Implementation Stop Conditions

다음 조건 중 하나라도 발생하면 Discord-1a implementation은 중단되어야 합니다.

- allowed files 밖 변경이 필요합니다.
- `.github/workflows/**` 변경이 필요합니다.
- GitHub write permission이 필요합니다.
- Discord token 또는 webhook secret을 문서나 code에 노출해야 합니다.
- OpenAI API automation 또는 Codex 자동 호출이 필요합니다.
- `@codex fix`, review-thread resolve, workflow rerun, auto-merge control, direct merge가 필요합니다.
- owner decision을 Codex가 임의로 확정해야 합니다.
- raw PR body, raw labels, raw diff, raw review comments, secret-like values를 Discord에 출력해야 합니다.
- live trading, exchange credentials, risk cap increase, model live promotion과 연결됩니다.

## Future Implementation PR Boundary

Future implementation PR은 이 문서의 decision records 중 필요한 항목이 `APPROVED_BY_OWNER` 상태로 변경된 뒤에만 시작할 수 있습니다.

Future implementation PR은 최소한 다음을 PR body에 포함해야 합니다.

- approved decision IDs
- allowed files
- non-goals
- permission boundary
- no-write or write-scope statement
- redaction policy
- source-of-truth revalidation order
- validation plan
- rollback or stop procedure

이 문서는 future implementation PR의 allowed files를 승인하지 않습니다. D1A-019가 owner-approved 상태가 되기 전까지 implementation file set은 `OWNER_DECISION_REQUIRED`입니다.

## Owner Sign-off Requirements

Owner sign-off는 명시적이어야 하며 다음을 포함해야 합니다.

- approved decision IDs
- selected option for each approved decision
- permissions allowed
- files allowed
- rollout level
- non-goals
- stop conditions

AI 또는 Codex는 owner sign-off를 대신 작성할 수 없습니다. AI는 필요한 decision을 요약할 수 있지만, 승인 문구를 생성해 owner approval처럼 취급하면 안 됩니다.

## Update Rules

- 이 문서는 Discord-1a implementation과 같은 PR에서 수정하지 않습니다.
- owner decision이 승인되면 해당 decision record를 별도 docs-only PR로 업데이트합니다.
- 승인된 decision은 `APPROVED_BY_OWNER`로 바꾸고, 승인 근거를 PR body 또는 commit context에서 추적 가능하게 남깁니다.
- rejected decision은 `REJECTED_BY_OWNER`로 바꾸고 구현 금지 이유를 기록합니다.
- 미정 항목은 `OWNER_DECISION_REQUIRED`로 유지합니다.
- committed docs에는 unfinished marker나 ambiguous placeholder를 남기지 않습니다.
