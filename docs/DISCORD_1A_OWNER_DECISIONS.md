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

이 문서의 v2 update는 Discord-1a notification-only 구현 전 필요한 최소 정책과 future first implementation PR boundary만 `APPROVED_BY_OWNER`로 기록합니다. 승인되지 않은 decision은 계속 `OWNER_DECISION_REQUIRED`, `Not approved`, `Implementation prohibited` 상태입니다.

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
| D1A-006 | audit log storage는 어디인가? | `APPROVED_BY_OWNER` | GitHub Actions run log and job summary with redacted metadata only | no persistent audit log store for v1 | Discord-1a v1은 별도 persistent audit log store를 만들지 않습니다. GitHub Actions run log와 GitHub Actions job summary에 redacted metadata만 남깁니다. raw PR body, raw diff, raw labels, raw comments, secret-like value, Discord webhook URL은 저장하지 않습니다. external log store는 승인하지 않습니다. | `Implementation prohibited` for any other audit storage | notification history와 incident review 가능성을 결정합니다. | persistent audit log store 또는 raw data 저장이 필요하면 구현 금지 | redacted metadata-only summary and no external log store |
| D1A-007 | idempotency key / dedup ledger storage는 어디인가? | `APPROVED_BY_OWNER` | stateless per-run dedup only | stateless per-run dedup only | Discord-1a v1은 persistent dedup ledger를 만들지 않습니다. v1은 stateless per-run dedup only로 제한합니다. duplicate notification 가능성은 v1에서 허용하되, Discord message에는 PR number, short head SHA, workflow run id를 포함해 사람이 중복을 식별할 수 있게 합니다. external storage, database, cache, GitHub write-back ledger는 승인하지 않습니다. | `Implementation prohibited` for persistent ledger | duplicate notification 방지 수준을 결정합니다. | persistent ledger, external storage, database, cache, GitHub write-back ledger가 필요하면 구현 금지 | stateless per-run dedup logic and message fields for manual duplicate recognition |
| D1A-008 | raw event retention policy 세부 기간은 무엇인가? | `APPROVED_BY_OWNER` | no raw event retention; redacted metadata only | no raw event retention | raw event retention은 하지 않습니다. raw PR body, raw diff, raw labels, raw comments, raw review text, raw Codex output은 저장하거나 Discord로 보내지 않습니다. redacted metadata only를 원칙으로 합니다. | `Implementation prohibited` for raw retention | PR body, raw labels, raw comments, raw diff 저장 여부와 기간을 결정합니다. | raw event retention 또는 raw text Discord 출력이 필요하면 구현 금지 | redacted metadata-only behavior |
| D1A-009 | redaction failure policy는 무엇인가? | `APPROVED_BY_OWNER` | fail closed | fail closed | redaction이 실패하거나 확신할 수 없으면 fail closed하고 Discord 전송을 하지 않습니다. | `Implementation prohibited` for any send-on-uncertain-redaction behavior | redaction 실패 시 Discord 출력 여부를 결정합니다. | uncertain redaction 상태에서 전송이 필요하면 구현 금지 | redaction test cases and failure behavior |
| D1A-010 | stale-state control policy는 무엇인가? | `APPROVED_BY_OWNER` | revalidate before send; suppress on mismatch | revalidate before send; suppress on mismatch | Discord 전송 직전에 GitHub source-of-truth를 재확인합니다. PR head SHA, PR state, relevant check state가 기대값과 다르면 전송하지 않습니다. | `Implementation prohibited` for stale-state send behavior | GitHub source states가 불일치할 때 동작을 결정합니다. | stale state에서 전송 또는 action이 필요하면 구현 금지 | revalidation order and stale-state examples |
| D1A-011 | rate limits의 정확한 수치는 무엇인가? | `APPROVED_BY_OWNER` | one Discord message per workflow run; fail closed on rate-limit response | one Discord message per workflow run | Discord-1a v1은 workflow run당 최대 1개의 Discord message만 전송합니다. Discord HTTP 429 또는 rate-limit 의심 응답을 받으면 retry storm을 만들지 않고 fail closed합니다. scheduled polling은 v1에서 승인하지 않습니다. persistent per-day counter는 만들지 않습니다. | `Implementation prohibited` for higher-volume notification behavior | spam과 API pressure를 제한합니다. | multiple messages per workflow run, scheduled polling, persistent counter, retry storm이 필요하면 구현 금지 | one-message-per-run guard and fail-closed 429 handling |
| D1A-012 | failure notification policy의 세부 fallback은 무엇인가? | `APPROVED_BY_OWNER` | no recursive Discord failure notification; redacted GitHub Actions summary/log only | no recursive Discord failure notification | Discord send 실패 시 Discord로 재귀적 failure notification을 보내지 않습니다. 실패 정보는 GitHub Actions job summary/log에 redacted failure summary로만 남깁니다. webhook failure, redaction uncertainty, stale-state mismatch, fork/external PR 감지는 모두 send suppression으로 처리합니다. 별도 escalation channel, GitHub Issue/comment, workflow rerun, auto-merge control은 승인하지 않습니다. | `Implementation prohibited` for fallback write path | webhook/API 실패 시 알림 방식을 결정합니다. | escalation channel, GitHub Issue/comment, workflow rerun, auto-merge control, recursive notification이 필요하면 구현 금지 | redacted job summary/log failure path and send suppression behavior |
| D1A-013 | fork/external PR notification policy는 무엇인가? | `APPROVED_BY_OWNER` | exclude fork/external PRs | exclude fork/external PRs | Discord-1a notification path에서도 fork/external PR은 제외합니다. | `Implementation prohibited` for fork/external PR notification path | untrusted external PR 상태를 Discord에 노출할지 결정합니다. | fork/external PR notification이 필요하면 구현 금지 | same-repo verification logic |
| D1A-014 | daily Codex request cap은 무엇인가? | `APPROVED_BY_OWNER` | zero automated Codex requests | zero automated Codex requests | Discord-1a의 automatic Codex request cap은 0입니다. Discord-1a는 Codex를 자동 호출하지 않습니다. | `Implementation prohibited` for automated Codex calls | Discord-1a가 Codex request를 유발하지 않도록 제한합니다. | automated Codex request가 필요하면 구현 금지 | enforcement showing no Codex call path |
| D1A-015 | Codex Review automation policy는 무엇인가? | `APPROVED_BY_OWNER` | no automation | no automation | Discord-1a는 Codex Review를 자동 호출하지 않습니다. Codex Review는 계속 advisory/manual 상태입니다. | `Implementation prohibited` for Codex Review automation | Codex Review를 notification path에 연결할지 결정합니다. | Codex Review automation이 필요하면 구현 금지 | no Codex Review call path |
| D1A-016 | automatic `@codex fix`를 허용할 것인가? | `APPROVED_BY_OWNER` | prohibited | prohibited | `Not approved`. Discord-1a에서 자동 `@codex fix`는 금지합니다. | `Implementation prohibited` for automatic fix flow | 자동 수정 loop 여부를 결정합니다. | automatic fix request가 필요하면 구현 금지 | no `@codex fix` call path |
| D1A-017 | review-thread resolve 자동화를 허용할 것인가? | `APPROVED_BY_OWNER` | prohibited | prohibited | `Not approved`. Discord-1a에서 review-thread resolve 자동화는 금지합니다. | `Implementation prohibited` for review-thread resolve automation | GitHub conversation resolution 권한 확장을 결정합니다. | automated resolve가 필요하면 구현 금지 | no resolveReviewThread call path |
| D1A-018 | post-merge lesson-loop prevention policy는 무엇인가? | `APPROVED_BY_OWNER` | no habitual merged-PR `@codex review`; separate post-merge lesson flow | no habitual merged-PR `@codex review`; separate post-merge lesson flow | merged PR에 습관적으로 `@codex review`를 호출하지 않습니다. post-merge lesson capture와 future lesson PR은 별도 flow로 유지합니다. | `Implementation prohibited` for automatic lesson-loop expansion | post-merge follow-up recursion 방지 수준을 결정합니다. | automatic post-merge review loop가 필요하면 구현 금지 | separate lesson flow and loop prevention statement |
| D1A-019 | Discord-1a implementation PR allowed files는 무엇인가? | `APPROVED_BY_OWNER` | split PR sequence; first implementation PR workflow file only | split PR sequence with one workflow file | Discord-1a first implementation PR은 split PR sequence의 첫 implementation PR로 제한합니다. first implementation PR allowed file은 `.github/workflows/discord-1a-notification.yml` 하나만 허용합니다. helper script, `src/**`, `tests/**`, docs update, prompt update, issue template update가 필요하면 first implementation PR을 중단하고 별도 owner decision을 받습니다. implementation PR은 GitHub Actions-only, read-only, notification-only여야 합니다. | `Implementation prohibited` for any additional implementation file | future implementation blast radius를 결정합니다. | allowed file 하나 밖 변경이 필요하면 구현 금지 | PR diff showing only `.github/workflows/discord-1a-notification.yml` |
| D1A-020 | owner sign-off approvers 확장 기준은 무엇인가? | `APPROVED_BY_OWNER` | repository owner only | repository owner only | Discord-1a v1 owner sign-off approver는 repository owner only로 제한합니다. backup approver, maintainer group, AI-generated approval은 승인하지 않습니다. | `Implementation prohibited` for expanded approver list | policy approval authority를 결정합니다. | repository owner 외 approval을 요구하면 구현 금지 | owner sign-off from repository owner |
| D1A-021 | health check / recovery playbook 세부 절차는 무엇인가? | `APPROVED_BY_OWNER` | manual recovery only | manual recovery only | Discord-1a v1은 manual recovery only입니다. 자동 복구, 자동 workflow rerun, 자동 GitHub comment, 자동 issue 생성, 자동 fix 요청은 승인하지 않습니다. 실패 시 owner는 GitHub Actions run summary/log와 GitHub source-of-truth를 직접 확인합니다. | `Implementation prohibited` for automated recovery | 장애 감지와 복구 자동화 범위를 결정합니다. | automated recovery, workflow rerun, GitHub comment, issue creation, fix request가 필요하면 구현 금지 | manual recovery notes in PR body |
| D1A-022 | future workflow trigger matrix는 무엇인가? | `APPROVED_BY_OWNER` | `workflow_dispatch` and trusted default-branch `workflow_run` only | `workflow_dispatch` and trusted default-branch `workflow_run` only | Discord-1a first implementation은 `workflow_dispatch`와 trusted default-branch `workflow_run` 기반 notification만 허용합니다. `workflow_run`은 Codex가 main의 실제 workflow names를 확인한 뒤 trusted workflow completion event만 대상으로 합니다. 후보 trusted workflows는 CI/checks workflow, AI Review Gate, Enable auto-merge, Post Merge Lesson Capture입니다. 실제 workflow name이 확인되지 않으면 implementation을 중단합니다. `pull_request_target`, `pull_request`, scheduled polling, repository_dispatch, issue_comment trigger는 v1에서 승인하지 않습니다. fork/external PR은 notification path에서도 suppress합니다. | `Implementation prohibited` for any unapproved trigger | 어떤 GitHub event에서 notification을 만들지 결정합니다. | unapproved trigger, unverified workflow name, fork/external PR notification이 필요하면 구현 금지 | verified workflow names from main and trigger allowlist |
| D1A-023 | future Discord message schema는 무엇인가? | `APPROVED_BY_OWNER` | compact redacted status summary only | compact redacted status summary only | Discord message는 compact redacted status summary만 허용합니다. 허용 field는 repository name, PR number, PR state, base branch, short head SHA, trusted workflow/check name, check conclusion/status, AI Review Gate verdict category if available, source-of-truth revalidation result, workflow run id, GitHub PR URL, owner action category from a fixed enum입니다. 금지 field는 raw PR title, raw PR body, raw diff, raw labels, raw comments, raw review text, raw Codex output, file contents, secret-like values, Discord webhook URL, trading signal, order, position, account, wallet, credential data입니다. owner action category는 `NO_ACTION`, `CHECK_SOURCE_OF_TRUTH`, `OWNER_DECISION_REQUIRED`, `STOPPED_POLICY`, `SUPPRESSED_STALE_STATE`, `SUPPRESSED_EXTERNAL_PR`, `SUPPRESSED_REDACTION_UNCERTAIN`만 허용합니다. | `Implementation prohibited` for any raw/unredacted schema | Discord에 표시할 field와 redaction boundary를 결정합니다. | raw/unredacted field가 필요하면 구현 금지 | message schema allowlist and denylist validation |

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

이 문서는 Discord-1a implementation 자체를 승인하지 않습니다. D1A-019는 future first implementation PR의 allowed file boundary만 승인합니다. Future first implementation PR이 진행될 경우 changed file은 `.github/workflows/discord-1a-notification.yml` 하나로 제한됩니다.

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
