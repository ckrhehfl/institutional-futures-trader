# Discord-1a Notification-only Plan

이 문서는 Discord-1a incoming webhook notification-only 단계의 구현 전 계약입니다. 이 문서는 구현이 아닙니다. Owner approval 전에는 Discord webhook sender, GitHub Actions workflow, Discord bot, slash command, GitHub App, OpenAI API automation, token handling code, 또는 GitHub write path를 추가하지 않습니다.

## Scope

Discord-1a의 범위는 GitHub source-of-truth 상태를 읽고 Discord에 redacted/read-only notification만 보내는 것입니다.

- Discord는 source of truth가 아닙니다.
- Discord message는 approval signal이 아닙니다.
- Discord message는 GitHub 원본 상태의 redacted/read-only status projection입니다.
- `MERGE_ELIGIBLE`은 Discord가 merge를 승인한다는 뜻이 아닙니다.
- Merge 판단은 기존 GitHub branch protection, CI, AI Review Gate, conditional auto-merge가 담당합니다.

읽기 대상 후보는 다음 GitHub source-of-truth 상태입니다.

- PR metadata
- PR state
- base branch
- head branch
- head SHA
- PR commit list
- changed files metadata
- check runs
- AI Review Gate status and artifact
- post-merge lesson capture status and artifact

Discord-1a에서 보낼 수 있는 알림은 다음처럼 read-only 상태 요약에 한정합니다.

- PR opened / updated / ready-for-review summary
- required checks completed summary
- AI Review Gate `PASS`, `FAIL`, `NEEDS_OWNER_POLICY` summary
- `MERGE_ELIGIBLE` or blocked summary
- PR merged summary
- post-merge lesson capture `LESSON_CANDIDATE_FOUND` or `NO_LESSON` summary

## Non-goals

- `.github/workflows/**` 변경 금지
- `.github/prompts/**` 변경 금지
- `.github/ISSUE_TEMPLATE/**` 변경 금지
- `AGENTS.md` 변경 금지
- `src/**`, `tests/**` 변경 금지
- `docs/DISCORD_OPERATOR_BRIDGE.md` 변경 금지
- GitHub Actions 구현 금지
- Discord webhook sender 구현 금지
- Discord slash command 구현 금지
- `/pm start`, `/pm status`, `/pm summary` 구현 금지
- GitHub Issue 생성 금지
- GitHub comment 작성 금지
- `@codex fix` 자동 호출 금지
- review-thread resolve 금지
- workflow rerun 금지
- auto-merge 제어 금지
- 직접 merge 금지
- GitHub App 구현 금지
- OpenAI API automation 금지
- GitHub write 권한 추가 금지
- live trading, exchange credentials, risk cap increase, model live promotion 연결 금지

## No-write Guarantee

Discord-1a는 GitHub 또는 repository에 아무것도 쓰지 않습니다.

- No issue creation
- No PR comments
- No labels
- No branch pushes
- No commits
- No pull request creation
- No workflow rerun
- No review-thread resolve
- No auto-merge enable/disable
- No direct merge

이 보장이 깨지는 요구가 생기면 Discord-1a 구현을 중단하고 owner decision을 요청해야 합니다.

## No-AI Guarantee

Discord-1a는 OpenAI API automation 또는 Codex request를 자동 발생시키지 않습니다.

- No OpenAI API call
- No Codex GitHub Action
- No automatic `@codex fix`
- No AI-generated owner signoff
- No AI-generated review-thread resolution

AI Review Gate artifact는 source-of-truth input으로 읽을 수 있지만, Discord-1a가 AI Review Gate를 실행하거나 재실행하지 않습니다.

## No-control Guarantee

Discord-1a는 control plane이 아니라 notification projection입니다.

- Branch protection을 변경하지 않습니다.
- CI를 변경하거나 재실행하지 않습니다.
- AI Review Gate를 변경하거나 재실행하지 않습니다.
- Conditional auto-merge를 arm/disarm하지 않습니다.
- Live trading gate를 변경하지 않습니다.
- Owner decision을 대신하지 않습니다.

## GitHub Source-of-truth Revalidation Order

Discord 알림이나 Codex 응답은 source of truth가 아닙니다. Discord-1a notification을 만들기 전에는 GitHub 원본 상태를 다음 순서로 재검증합니다.

1. PR number
2. PR state: open, closed, merged
3. base branch
4. head branch
5. same-repo or fork/external status
6. head SHA
7. PR commit list
8. changed files metadata
9. allowed/high-risk path category summary
10. check runs and conclusions
11. AI Review Gate status and artifact
12. post-merge lesson capture status and artifact
13. owner-policy state, including `OWNER_SIGNOFF_REQUIRED` or `STOPPED_POLICY`

If GitHub source states disagree, Discord-1a should send at most a redacted stale-state warning and must not trigger any write action.

## Redaction Policy

All PR-derived text is untrusted. PR title is also untrusted text.

Allowed Discord output:

- PR number
- sanitized title
- GitHub source link
- source timestamp
- workflow run ID or check run ID
- short head SHA
- current state
- status summary
- redacted label summary
- changed-file count
- allowlisted path summary
- high-risk path category
- next required human action summary

Forbidden Discord output:

- raw PR title when unsanitized
- raw PR body
- raw labels
- raw diff
- raw review comments
- raw file path list when unnecessary or sensitive
- secrets, tokens, API keys
- account IDs
- wallet addresses
- environment values
- webhook URL
- untrusted user text 원문
- raw exchange payloads

If a safe redacted summary cannot be produced, the notification should be skipped or replaced with a generic `redaction_blocked` status.

## Fork / External PR Redaction Policy

Fork or external PR content is untrusted text data.

For fork/external PRs, Discord-1a must not output:

- raw title
- raw body
- raw labels
- raw diff
- raw comments
- raw file paths

Allowed fork/external summary is limited to:

- PR number
- source timestamp
- fork/external status
- short head SHA when safe
- check status summary
- AI Review Gate status summary
- generic changed-file count
- generic high-risk category, if detected from metadata
- link to GitHub source of truth

Fork/external PR handling must not create any write path.

## Notification Format Examples

### AI Review Gate Owner Policy

```text
[AI Review Gate] PR #30
State: OWNER_SIGNOFF_REQUIRED
Source: run 123456789, head daa10bf
Summary: Policy decision needed before further automation.
Owner action: confirm approved scope / rollout / permissions in GitHub.
Link: https://github.com/.../pull/30
```

### Checks Passed

```text
[Checks] PR #31
State: MERGE_ELIGIBLE
Source: run 123456790, head abcd123
Summary: Required checks passed. Discord is not approving merge.
Next: GitHub branch protection, CI, AI Review Gate, and conditional auto-merge decide.
Link: https://github.com/.../pull/31
```

### Post-merge Lesson Capture

```text
[Post-merge Lesson Capture] PR #32
State: NO_LESSON
Source: artifact run 123456791, merge ef56789
Summary: No durable lesson candidate found.
Next: No follow-up needed.
Link: https://github.com/.../actions/runs/123456791
```

### Stale State

```text
[Notification] PR #33
State: STOPPED_STALE_OR_INCONSISTENT_STATE
Source: head 123abcd
Summary: GitHub source states disagree. No action taken.
Owner action: inspect GitHub PR/check/artifact directly.
Link: https://github.com/.../pull/33
```

## Dedup / Idempotency Key Design

Discord-1a should avoid repeated notifications for the same observed state.

Suggested keys:

- PR/check events: `event_type + pr_number + head_sha + run_id + conclusion`
- AI Review Gate: `ai_review_gate + pr_number + head_sha + run_id + verdict`
- post-merge lesson: `source_pr_number + merge_sha + lesson_slug`
- stale state: `stale_state + pr_number + head_sha + reason_code`

Dedup/idempotency ledger 저장 위치는 확인 필요입니다. Ledger 저장 위치가 확정되지 않으면 Discord-1a 구현을 시작하지 않습니다.

## Failure Classes And Stop Policy

Failure classes:

- `WEBHOOK_DELIVERY_FAILED`: Discord webhook delivery failed
- `DISCORD_RATE_LIMITED`: Discord webhook rate limit
- `GITHUB_API_FAILED`: GitHub source-of-truth read failed
- `ARTIFACT_UNAVAILABLE`: AI Review Gate or post-merge artifact unavailable
- `STALE_OR_INCONSISTENT_STATE`: GitHub source states disagree
- `REDACTION_BLOCKED`: safe summary cannot be produced without raw/untrusted output
- `OWNER_POLICY_REQUIRED`: owner approval is needed before implementation or operation

Failure policy:

- Do not write to GitHub.
- Do not retry in a tight loop.
- Do not post PR comments or Issues.
- Do not rerun workflows.
- Do not trigger Codex.
- Repeated failures should be rate-limited and summarized.
- If safe notification cannot be produced, skip the notification.

## Cost / Rate Limiting

Discord-1a should have near-zero AI cost.

- No OpenAI API usage
- No automatic Codex requests
- No model routing changes
- GitHub API reads should be bounded per event
- Discord webhook sends should respect Discord rate limits
- Duplicate state notifications should be deduped
- Daily Codex request cap remains a future owner decision

Suggested rate limits:

- same PR / same state / same head SHA: notify once
- repeated delivery failure: notify at most once per configured window
- post-merge lesson capture: notify final state only

Exact rate limit values are owner decisions.

## Security / Permissions

Discord-1a should use read-only GitHub access only.

Forbidden permissions:

- `contents: write`
- `pull-requests: write`
- `issues: write`
- `actions: write`
- `administration`
- branch protection write
- secrets read/write
- workflow rerun permission

Security requirements:

- Webhook URL is a secret and must never be logged, printed, or sent to Discord.
- Webhook URL storage and rotation are 확인 필요.
- Discord channel access scope is 확인 필요.
- Audit log storage is 확인 필요.
- Fork/external PR notification must be redacted summary only.
- Live trading, credentials, risk cap increase, and model live promotion are hard stop boundaries.

## Owner Decisions Required

Owner approval is required before implementation.

- Discord webhook URL 저장/회전 방식
- Discord 알림 채널/접근자 범위
- raw event retention policy
- audit log 저장 위치
- idempotency/dedup ledger 저장 위치
- rate limit 기준
- failure notification policy
- hosting 방식
- GitHub Actions 기반인지 외부 hosting 기반인지
- Discord-1a 구현 PR에서 허용할 파일 목록
- fork/external PR 알림 허용 범위
- daily Codex request cap

If these decisions are not recorded, implementation is prohibited.

## Validation Plan

Planning/document-only validation:

- `git diff --check`
- `git status --short --untracked-files=all`
- `git diff --name-only origin/main..HEAD`
- `pre-commit run --all-files --show-diff-on-failure`

Future implementation validation candidates:

- no-write permission check
- webhook URL non-disclosure check
- redaction test for PR title/body/labels/diff/comments/file paths
- fork/external PR redaction test
- dedup/idempotency test
- rate-limit behavior test
- webhook failure test
- GitHub API failure test
- artifact unavailable test
- stale/inconsistent state test
- AI Review Gate / CI / branch protection / auto-merge independence check
- live trading / credentials / risk cap / model promotion boundary check

## Stop Conditions

Stop and request owner decision if any of these occur:

- GitHub write permission is needed
- webhook URL storage/rotation is not decided
- Discord channel access scope is not decided
- audit log storage is not decided
- dedup/idempotency ledger storage is not decided
- raw PR body/diff/comment/labels/file paths must be output
- workflow rerun is needed
- merge or auto-merge control is needed
- OpenAI API automation is needed
- `@codex fix` automation is needed
- review-thread resolve is needed
- live trading, exchange credentials, risk cap increase, or model live promotion is touched
- GitHub source state is stale or inconsistent
- AI Review Gate returns `NEEDS_OWNER_POLICY`

## Future Implementation PR Boundary

The implementation PR allowed files are not approved by this document. They must be decided by the owner after hosting and secret storage decisions are made.

Possible future implementation shapes:

- GitHub Actions based notification
- external hosting based notification
- docs-only refinement before implementation

All are 확인 필요. No implementation may begin before owner approval.

Owner approval before implementation.
