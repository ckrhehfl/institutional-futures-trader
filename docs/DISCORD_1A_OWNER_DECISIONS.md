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
| `APPROVED_BY_OWNER` | owner가 future PR에서 명시적으로 승인한 상태입니다. 이 문서에서는 사용하지 않습니다. |
| `REJECTED_BY_OWNER` | owner가 future PR에서 명시적으로 거부한 상태입니다. 이 문서에서는 사용하지 않습니다. |

이 문서에서는 모든 required decision의 현재 상태가 `OWNER_DECISION_REQUIRED`입니다.

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

아래 decision records는 모두 다음 공통 상태를 가집니다.

- Current status: `OWNER_DECISION_REQUIRED`
- Approved decision: `Not approved`
- Default until approved: `Implementation prohibited`

| Decision ID | Question | Allowed options | Recommended option, if any | Implementation impact | Stop condition | Evidence required before implementation |
| --- | --- | --- | --- | --- | --- | --- |
| D1A-001 | Discord webhook URL storage / rotation을 어디에 두고 어떻게 회전할 것인가? | GitHub Actions secret, external secret manager, manually rotated owner-held secret | external secret manager 또는 GitHub Actions secret 중 owner가 선택 | secret storage와 rotation process를 결정합니다. | storage와 rotation owner가 승인되지 않으면 구현 금지 | approved storage path, rotation cadence, emergency revocation process |
| D1A-002 | Discord channel access scope를 어떻게 제한할 것인가? | owner-only private channel, limited operator channel, read-only audit channel | owner-only private channel에서 시작 | 누가 notification을 볼 수 있는지 결정합니다. | channel membership boundary가 승인되지 않으면 구현 금지 | approved channel, allowed viewers, access review cadence |
| D1A-003 | hosting model은 무엇인가? | GitHub Actions, external hosting, manually triggered local sender | GitHub Actions 또는 external hosting 중 owner가 선택 | runtime location, secret exposure, audit path를 결정합니다. | hosting model이 승인되지 않으면 구현 금지 | approved hosting model, runtime owner, failure isolation notes |
| D1A-004 | GitHub Actions 기반인지 external hosting 기반인지 어떻게 선택할 것인가? | GitHub Actions only, external hosting only, phased comparison | phased comparison | implementation file set과 permission model을 결정합니다. | platform choice가 승인되지 않으면 구현 금지 | selected platform, allowed files, operational boundary |
| D1A-005 | GitHub read identity / permission boundary는 무엇인가? | `contents: read`, `pull-requests: read`, `checks: read`, external read-only token | read-only identity only | GitHub API read scope를 결정합니다. | write permission이 필요하면 구현 금지 | permission list proving no write access |
| D1A-006 | audit log storage는 어디인가? | GitHub Actions artifact, external log store, no persistent audit log for v1 | GitHub Actions artifact 또는 no persistent audit log for v1 중 owner가 선택 | notification history와 incident review 가능성을 결정합니다. | storage location과 retention이 승인되지 않으면 구현 금지 | log location, retention policy, redaction guarantee |
| D1A-007 | idempotency key / dedup ledger storage는 어디인가? | GitHub Actions artifact, external storage, stateless per-run dedup only | stateless per-run dedup only에서 시작 | duplicate notification 방지 수준을 결정합니다. | ledger storage가 승인되지 않으면 persistent dedup 구현 금지 | key format, storage path, retention policy |
| D1A-008 | raw event retention policy는 무엇인가? | no raw event retention, redacted metadata only, owner-approved temporary retention | no raw event retention | PR body, raw labels, raw comments, raw diff 저장 여부를 결정합니다. | raw event retention이 필요하면 구현 금지 | retention policy proving raw sensitive text is not stored |
| D1A-009 | redaction failure policy는 무엇인가? | fail closed, send redacted error only, suppress notification | fail closed | redaction 실패 시 Discord 출력 여부를 결정합니다. | raw text 출력이 필요하면 구현 금지 | redaction test cases and failure behavior |
| D1A-010 | stale-state control policy는 무엇인가? | suppress stale notification, send stale-state warning, fail closed | send stale-state warning with no write action | GitHub source states가 불일치할 때 동작을 결정합니다. | stale state에서 action이 필요하면 구현 금지 | revalidation order and stale-state examples |
| D1A-011 | rate limits는 무엇인가? | per-PR cap, per-hour cap, per-day cap, backoff on Discord 429 | per-hour and per-day cap | spam과 API pressure를 제한합니다. | cap이 승인되지 않으면 구현 금지 | numeric caps and backoff behavior |
| D1A-012 | failure notification policy는 무엇인가? | suppress repeated failures, send redacted failure summary, owner-only escalation | redacted failure summary with repetition cap | webhook/API 실패 시 알림 방식을 결정합니다. | failure loop 가능성이 있으면 구현 금지 | failure classes, retry count, suppression rules |
| D1A-013 | fork/external PR notification policy는 무엇인가? | suppress notification, redacted minimal summary, owner-only summary | redacted minimal summary | untrusted external PR 상태를 Discord에 얼마나 노출할지 결정합니다. | raw title/body/labels/file paths/comments/diff 출력이 필요하면 구현 금지 | allowed summary fields and redaction examples |
| D1A-014 | daily Codex request cap은 무엇인가? | zero automated Codex requests, numeric daily cap, owner-triggered only | zero automated Codex requests for Discord-1a | Discord-1a가 Codex request를 유발하지 않도록 제한합니다. | automated Codex request가 필요하면 구현 금지 | cap value and enforcement location |
| D1A-015 | Codex Review automation policy는 무엇인가? | no automation, manual sampling only, report-only future experiment | no automation | Codex Review를 notification path에 연결할지 결정합니다. | Codex Review automation이 필요하면 구현 금지 | owner-approved sampling and reporting policy |
| D1A-016 | automatic `@codex fix`를 허용할 것인가? | prohibited, owner-triggered only, future guarded flow | prohibited | 자동 수정 loop 여부를 결정합니다. | automatic fix request가 필요하면 구현 금지 | explicit owner approval and loop guard design |
| D1A-017 | review-thread resolve 자동화를 허용할 것인가? | prohibited, owner-triggered only, future optional feature | prohibited | GitHub conversation resolution 권한 확장을 결정합니다. | automated resolve가 필요하면 구현 금지 | permission review and owner policy approval |
| D1A-018 | post-merge lesson-loop prevention policy는 무엇인가? | no automatic lesson PR, manual ce-compound only, future guarded babysitter | manual ce-compound only | post-merge follow-up recursion 방지 수준을 결정합니다. | automatic lesson PR이 필요하면 구현 금지 | idempotency key and recursion stop rules |
| D1A-019 | Discord-1a implementation PR allowed files는 무엇인가? | docs-only, single workflow, external sender files, split PR sequence | split PR sequence after owner approval | future implementation blast radius를 결정합니다. | allowed files가 승인되지 않으면 구현 금지 | approved file list and non-goals |
| D1A-020 | owner sign-off approvers는 누구인가? | repository owner only, named maintainers, owner plus backup approver | repository owner only until expanded | policy approval authority를 결정합니다. | approver list가 승인되지 않으면 구현 금지 | approver list and sign-off format |
| D1A-021 | health check / recovery playbook boundary는 무엇인가? | manual recovery only, notification-only health check, future automated recovery | manual recovery only | 장애 감지와 복구 자동화 범위를 결정합니다. | automated recovery가 필요하면 구현 금지 | recovery steps and no-write guarantee |

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
