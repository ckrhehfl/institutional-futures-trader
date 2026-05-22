# Discord Operator Bridge

이 문서는 Discord 기반 AI PM Operator Bridge의 설계 경계를 정의합니다. 이번 문서는 설계 문서이며 Discord bot, GitHub Actions workflow, OpenAI API automation, GitHub App, webhook server, command handler, token handling code를 구현하지 않습니다.

## Purpose

Discord Operator Bridge의 목적은 Discord를 operator console로 사용해 사람이 반복 지시를 덜 하면서도 GitHub와 Codex 기반 작업 루프를 안전하게 조율하는 것입니다.

- Discord는 operator console이지만 source of truth가 아닙니다.
- Discord는 GitHub 원본 상태의 redacted/read-only projection만 표시합니다.
- GitHub Issues, pull requests, review comments, labels, checks, PR commit list, remote branch head SHA, changed files, AI Review Gate artifacts, post-merge artifacts가 source of truth입니다.
- Codex Cloud/GitHub integration은 planning, implementation, review, fix loop의 worker입니다.
- CI, AI Review Gate, branch protection, conditional auto-merge는 hard gates입니다.

Discord와 PM Orchestrator는 직접 code edit, branch push, merge, live trading enablement를 수행하지 않습니다.

## Non-Goals

- Discord bot 구현 금지
- GitHub Actions workflow 구현 금지
- OpenAI API automation 추가 금지
- Codex GitHub Action 추가 금지
- GitHub App 구현 금지
- webhook, server, command handler, token handling code 구현 금지
- Discord에서 직접 code 수정 금지
- Discord에서 직접 merge 금지
- v1에서 `contents: write`, `pull-requests: write`, `actions: write`, `administration` 권한 사용 금지
- branch protection, AI Review Gate, auto-merge workflow, model routing 수정 금지
- `@codex fix` 자동화 구현 금지
- review-thread resolve 자동화 구현 금지
- PR watcher/babysitter 구현 금지
- post-merge babysitter 구현 금지
- live trading, exchange credentials, risk cap increase, model live promotion 자동화 금지
- OMS, Risk runtime, BingX REST/WebSocket, strategy, ML, trading engine, live trading 구현 금지

## Relationship to AI Operator Loop

`docs/AI_OPERATOR_LOOP.md`가 상위 운영 원칙입니다. Discord Operator Bridge는 그 원칙을 Discord entrypoint에 적용하는 하위 설계입니다.

- 사람은 code quality reviewer가 아닙니다.
- 사람은 cost limit, direction, hard prohibitions, summary confirmation, anomaly checks의 owner입니다.
- AI/Codex, deterministic checks, CI, AI Review Gate, policy gates가 technical review와 merge readiness를 가능한 한 많이 담당합니다.
- 사람이 Discord에서 내리는 명령은 scope, cost, prohibition, escalation에 관한 operator action이어야 합니다.

## Discord As Redacted Projection

Discord는 source of truth가 아닙니다. Discord message는 GitHub 원본 상태를 사람이 빠르게 읽을 수 있게 줄인 redacted/read-only projection입니다.

Source of truth는 다음 GitHub 원본 상태입니다.

- GitHub Issue and PR metadata
- PR commit list
- remote branch head SHA
- changed files metadata
- check runs and conclusions
- AI Review Gate summary and artifacts
- post-merge lesson capture artifacts
- owner comments and PR body policy decisions

Discord summary는 원본 텍스트를 복사하지 않고 검증 가능한 요약을 우선 표시합니다.

- GitHub source link
- source timestamp
- PR number or Issue number
- workflow run ID when available
- current head SHA when safe
- changed-file count
- allowlisted path summary
- high-risk path category summary
- check and gate conclusion summary

Discord에 그대로 출력하지 않는 값은 다음과 같습니다.

- raw PR body
- raw labels
- raw file paths from PR input
- raw diffs
- raw review comments
- raw secret-like values
- account IDs
- wallet addresses
- environment values
- raw exchange payloads

## Source-Of-Truth And Stale-State Controls

Codex 답변, Discord 알림, GitHub UI 요약만으로 다음 action을 진행하지 않습니다. Future action 전에는 GitHub source of truth를 다시 확인해야 합니다.

Before any future action, re-verify:

- PR open/merged state
- base branch
- same-repo/fork status
- remote head SHA
- changed files metadata
- allowed files / layers
- high-risk path and rename metadata
- CI status
- AI Review Gate status and artifact
- owner-policy state
- post-merge artifact status when applicable

If source states disagree, the bridge should move to `STOPPED_STALE_OR_INCONSISTENT_STATE` and wait for owner or operator review. Stale Discord messages do not authorize new actions.

## Command Catalog

These commands describe future semantics. They are not implemented by this PR.

### `/pm start`

GitHub Issue task contract 생성을 시작합니다.

- Required input: task summary, Scope, Non-goals, Allowed files / layers, Validation plan, Risk boundary, Owner decision points
- Output: GitHub Issue URL 또는 생성 실패 summary
- Discord-2b 이전 단계에서는 설계 후보일 뿐이며 실제 Issue 생성은 구현하지 않습니다.
- `/pm start` remains after read-only `/pm status` and `/pm summary` phases.
- Codex task 시작 방식은 owner decision이 필요한 항목입니다.

### `/pm status`

AI-managed task 또는 PR의 현재 상태를 요약합니다.

- Shows: state, GitHub Issue/PR URL, checks, AI Review Gate verdict, sanitized or redacted labels, blocker summary, last activity age
- Shows only summarized changed-file count, allowlisted path summary, and high-risk path category instead of raw file paths.
- Does not show: raw secrets, raw PR body, raw labels, raw file paths, raw review comments, raw untrusted diff text
- Does not change: PR, branch, labels, comments, merge state

### `/pm pause`

특정 task의 AI fix loop와 watcher action을 멈춥니다.

- Allows: read-only status updates
- Blocks: new `@codex fix` requests, new automation actions
- Does not disable: CI, AI Review Gate, branch protection

### `/pm resume`

pause된 task를 다시 진행 후보로 만듭니다.

- Before resume, re-check source-of-truth state and stop conditions.
- Do not resume if a hard prohibition, owner decision, cost stop, live boundary stop, stale-state stop, or permission stop is active.

### `/pm stop`

AI-managed loop를 종료합니다.

- Intended for normal cancellation or owner stop.
- Does not directly close PRs, delete branches, or revert commits in v1.
- Follow-up cleanup remains an owner decision.

### `/pm summary`

사람이 읽기 위한 compact summary를 생성합니다.

- Includes: task goal, current state, changed file categories, checks, review triage, cost signal, next owner action
- Excludes: raw PR title/body/labels/file paths when they may contain untrusted or secret-like data

### `/pm emergency-stop`

hard prohibition이나 security boundary가 의심될 때 즉시 멈춥니다.

Triggers include:

- secret, token, API key, account id, wallet address exposure
- live trading boundary contact
- exchange credentials request
- risk cap increase request
- model live promotion request
- unexpected workflow/security file changes
- branch protection bypass attempt

## Operating Levels and Rollout

### Discord-0: Design Doc Only

- Add the initial design document only.
- No Discord bot, workflow, token, webhook, server, or API automation.

### Discord-0a: Safety Hardening Document Update

- Strengthen this design before autonomous operation is considered.
- Add source-of-truth, push verification, owner-policy stop, redaction, post-merge chain, and loop-prevention guidance.
- No implementation, workflow, webhook, server, token, or permission change.

### Discord-1a: Incoming Webhook Notification-Only

- Implemented as notification-only workflow; this design document does not modify workflow behavior.
- Discord may receive redacted summaries through an incoming webhook after a future owner decision.
- No GitHub write.
- No slash commands.
- No `@codex fix`.
- No review-thread resolve.
- No PR comments, labels, branch updates, commits, merges, or issue creation.

### Discord-1b: Read-Only Source-of-Truth Summarizer

- Discord-1b는 Discord-1a를 대체하지 않고 보완하는 read-only summarizer boundary입니다.
- command path, slash command, bot handler를 포함하지 않습니다.
- GitHub source-of-truth 재검증과 redaction policy를 문서로 고정하며 구현은 별도 owner decision 이후로 미룹니다.

### Discord-1c: Post-Merge Lesson Capture Notification

- Notify whether post-merge lesson capture produced `LESSON_CANDIDATE_FOUND` or `NO_LESSON`.
- Do not create issues, comments, commits, branches, or PRs.

### Discord-2a: `/pm status` And `/pm summary` Read-Only Slash Commands

- Slash commands may request redacted status and summary only.
- No write action.
- No `@codex fix` request.

### Discord-2b: `/pm start` Creates GitHub Issue

- `/pm start` may create a GitHub Issue using the repository task contract only after owner approves Issues write.
- The Issue remains the source of truth.
- Starting Codex work from the Issue is confirmation needed.

### Discord-3a: Read-Only PR Watcher

- Watch PR metadata, checks, AI Review Gate result, labels, review comments, and owner commands.
- Prefer read-only permissions.
- Do not request fixes automatically.

### Discord-3b: Guarded `@codex fix` Request Flow

- Consider guarded `@codex fix` requests only after branch-push behavior and permissions are validated.
- Require source-of-truth re-verification, loop guard checks, and allowed-files checks before every request.
- `@codex fix` branch-push behavior in this repository is confirmation needed.

### Discord-3c: Review-Thread Resolve

- Optional and owner-approved only.
- Not part of v1.
- GitHub conversation resolution can affect merge gates, so automatic resolve requires a separate permission and policy decision.

### Discord-4a: Post-Merge Babysitter / ce-compound Handoff

- Track post-merge lesson capture output and recommend `/ce-compound` or docs-only follow-up only when appropriate.
- Do not auto-create docs commits, issues, comments, branches, or PRs without a future owner decision.

### Discord-4b: Docs-Only Lesson PR Babysitter

- Watch docs-only lesson PRs with loop prevention.
- Avoid recursively creating lessons about lessons unless a new operational incident occurred.

### Discord-5: Advanced Dashboards / Queues

- Possible additions: queue view, cost dashboard, richer owner summaries, stricter escalation reports.
- Live trading automation remains prohibited.

## State Machine

Primary states:

- `IDLE`: no managed task
- `TASK_CREATED`: GitHub Issue task contract exists
- `TASK_CONTEXT_VALIDATING`: source-of-truth and task contract are being checked before work starts
- `CODEX_STARTED`: Codex work was requested
- `PR_OPENED`: pull request exists
- `REVIEWING`: review, CI, or AI Review Gate is active
- `FIXING`: in-scope fix request is active
- `CODEX_PUSH_VERIFYING`: verifying that Codex's reported commit or fix actually reached the PR branch
- `WAITING_FOR_CHECKS`: waiting for CI, AI Review Gate, or branch protection
- `MERGE_ELIGIBLE`: required checks pass and no blocking stop condition is active
- `AUTO_MERGE_ARMED`: existing conditional auto-merge has been enabled and is waiting on GitHub branch protection
- `MERGED`: PR merged; this is not terminal
- `POST_MERGE_DETECTED`: merge was detected from GitHub source of truth
- `POST_MERGE_CAPTURE_RUNNING`: post-merge lesson capture workflow or equivalent report is running
- `LESSON_CANDIDATE_FOUND`: post-merge report found a durable lesson candidate
- `NO_LESSON`: post-merge report found no durable lesson; this is a normal result
- `LESSON_PR_OPENED`: a docs-only lesson PR exists after explicit owner or operator action
- `LESSON_PR_WAITING_FOR_CHECKS`: lesson PR is waiting for required checks
- `LESSON_PR_MERGED`: lesson PR merged
- `DONE`: operator loop is complete

Pause / policy states:

- `OWNER_SIGNOFF_REQUIRED`: owner policy decision is needed; no repeated AI fix loop is allowed
- `PAUSED_OWNER`: owner paused the task or requested no further automation

Stop states:

- `STOPPED_POLICY`: owner policy decision is missing, stale, conflicting, or rejected
- `STOPPED_PERMISSION_REQUIRED`: the next action requires permissions not approved for the current rollout level
- `STOPPED_STALE_OR_INCONSISTENT_STATE`: source-of-truth checks disagree or stale state is detected
- `STOPPED_COST`: cost limit or cost anomaly reached
- `STOPPED_LOOP_LIMIT`: loop guard exceeded
- `STOPPED_ALLOWED_FILES`: allowed files / layers violation detected
- `STOPPED_LIVE_BOUNDARY`: live trading, credentials, risk cap, or model promotion boundary touched
- `STOPPED_CODEX_FAILED`: Codex branch push, review, or fix action failed
- `STOPPED_CONFLICT`: merge conflict or incompatible branch state detected

`MERGE_READY` should not be used as a single state. The design distinguishes `MERGE_ELIGIBLE` from `AUTO_MERGE_ARMED` so the operator can tell whether a PR merely qualifies for merge or whether GitHub auto-merge has actually been armed.

Review-thread resolve is not part of the default state machine. It is a future Discord-3c owner-approved optional action only.

## Codex Push Verification

Codex saying "committed", "fixed", or "pushed" is not enough evidence that the PR branch was updated. A local commit or agent report is different from a verified remote PR branch update.

Before moving from `FIXING` to `WAITING_FOR_CHECKS`, the bridge must enter `CODEX_PUSH_VERIFYING` and verify:

- the expected commit appears in the PR commit list
- the remote PR branch head SHA equals the expected SHA
- changed files remain within the allowed files / layers
- workflow/security/live-boundary files were not touched unexpectedly
- no source/test/runtime/trading files were touched unless explicitly allowed by the task contract

If verification fails, move to `STOPPED_CODEX_FAILED`. Do not proceed to checks, AI Review Gate, merge eligibility, or auto-merge arming before push verification succeeds.

## Owner-Policy And `STOPPED_POLICY`

AI Review Gate `FAIL` and `NEEDS_OWNER_POLICY` are not repeated fix targets.

- AI Review Gate `FAIL` stops the loop unless the failure clearly maps to an in-scope document or implementation correction.
- AI Review Gate `NEEDS_OWNER_POLICY` transitions to `OWNER_SIGNOFF_REQUIRED`.
- If owner signoff is absent, stale, ambiguous, or conflicts with the approved scope, transition to `STOPPED_POLICY`.
- AI may summarize the missing owner decision, but AI must not write owner signoff on behalf of the owner.

Owner signoff should be recorded in PR body or owner comment and include:

- approved scope
- approved rollout level
- approved permissions, if any
- explicit non-goals
- whether the work is design-only or implementation
- any future decisions that remain unapproved

## Post-Merge Chain And Lesson-Loop Prevention

`MERGED` is not terminal. After a PR merges, the operator loop should continue through post-merge lesson capture before reaching `DONE`.

Post-merge chain:

- `MERGED`
- `POST_MERGE_DETECTED`
- `POST_MERGE_CAPTURE_RUNNING`
- `LESSON_CANDIDATE_FOUND` or `NO_LESSON`
- `LESSON_PR_OPENED`
- `LESSON_PR_WAITING_FOR_CHECKS`
- `LESSON_PR_MERGED`
- `DONE`

If no durable lesson candidate exists, `NO_LESSON` is a normal successful result and the loop may proceed to `DONE`.

Lesson loop prevention:

- docs/solutions-only lesson PRs default to `NO_LESSON` unless a new operational incident occurred.
- Use an idempotency key shaped as `source_pr_number + merge_sha + lesson_slug`.
- A future dedup ledger is needed before automating lesson PR follow-up, but this PR does not implement one.
- Lesson PR automation must not recursively create lessons about routine lesson PRs.

## PM Watcher / PR Babysitter Design

This section describes future design only. This PR does not implement a watcher or babysitter.

The watcher observes GitHub metadata only. It should watch:

- GitHub Issue state and task contract fields
- PR metadata and sanitized labels
- PR changed file metadata
- CI check conclusions
- AI Review Gate output and artifacts
- review comments and unresolved thread counts
- owner commands and policy comments
- auto-merge eligibility state
- post-merge lesson capture artifacts

The watcher must not:

- checkout PR head code
- build PR head code
- run PR head code
- install PR dependencies
- import PR code
- execute Discord text, Issue body, PR body, comments, labels, file paths, or diffs
- print raw PR text or raw file paths to Discord

Discord text, GitHub Issue body, PR body, comments, labels, file names, and diffs are untrusted text data.

`@codex fix` may be considered only when all of these are true:

- the review item is `IN_SCOPE_BUG` or `IN_SCOPE_DOC_OR_TEST_FIX`
- the fix stays inside the Issue/PR Allowed files / layers
- source-of-truth state has been freshly verified
- loop guards have not been exceeded
- no stop condition is active
- no live trading, credential, risk cap, or model promotion boundary is touched
- Codex branch-push behavior and required permissions have been validated

`@codex fix` branch-push behavior in this repository is confirmation needed until validated.

## Review-Thread Resolve Policy

Review-thread resolve is prohibited in v1.

Resolved or outdated review feedback does not automatically mean automation may resolve the GitHub conversation. GitHub conversation resolution can affect merge gates and reviewer visibility, so automatic resolve is a future owner-approved optional feature only.

Before any review-thread resolve automation is considered, the owner must decide:

- who may resolve threads
- whether only outdated threads may be auto-resolved
- whether owner-policy threads are excluded
- what audit trail is required
- what permissions the automation needs
- whether GraphQL `resolveReviewThread` automation is allowed

This belongs no earlier than Discord-3c.

## Auto-Merge Boundary

- Discord never directly merges.
- PM Orchestrator never directly merges.
- Existing conditional auto-merge remains the only merge automation path.
- No `--admin`.
- No branch protection bypass.
- CI and AI Review Gate remain required checks.
- `MERGE_ELIGIBLE` means the PR appears eligible according to source-of-truth checks.
- `AUTO_MERGE_ARMED` means existing GitHub conditional auto-merge has been enabled and is waiting on branch protection.
- Live trading enablement is separate from main branch merge automation.

## Permission Model

- Discord-0: no permissions
- Discord-0a: no permissions
- Discord-1a: incoming webhook notification-only, no GitHub write
- Discord-1b: read-only metadata access for PR/check/AI Gate summaries
- Discord-1c: read-only post-merge lesson capture notification
- Discord-2a: read-only slash command status and summary may be considered
- Discord-2b: GitHub Issues write may be considered only after a later owner decision
- Discord-3a: PR watcher should prefer read permissions
- Discord-3b: `@codex fix` request permissions are confirmation needed
- Discord-3c: review-thread resolve permissions are confirmation needed
- Discord-4a/4b: post-merge babysitter permissions are confirmation needed

v1 avoids:

- `contents: write`
- `pull-requests: write`
- `actions: write`
- `administration`
- secrets access
- branch protection changes
- repository secret reads or writes
- GraphQL review-thread resolve permissions

Any write permission expansion requires an owner decision before implementation.

## Loop Guards

- `max_fix_attempts_per_pr = 3`
- `max_same_failure_repeats = 2`
- `max_ai_commits_per_pr = 5`
- `max_open_ai_managed_prs = 2`
- `max_task_age_hours = 24`
- `max_codex_requests_per_day = owner-configured`

Loop guard counters should be evaluated before requesting another AI action.

## Stop Conditions

Stop the loop when any of these occur:

- same check fails twice for the same reason
- AI Review Gate returns `FAIL` once unless it maps to a concrete in-scope fix
- AI Review Gate returns `NEEDS_OWNER_POLICY` once
- owner signoff is missing, stale, or conflicts with scope
- allowed files / layers violation
- live trading, credentials, risk cap, or model promotion detected
- unexpected workflow/security file changes
- source-of-truth state is stale or inconsistent
- required permission is not approved
- merge conflict
- Codex branch push verification failure
- auto-merge blocked too long
- cost limit reached
- PR scope conflicts with Issue task contract
- `@codex fix` proposes or pushes out-of-scope changes

After a stop condition, the bridge reports a redacted summary and waits for owner direction. It does not keep fixing.

## Idempotency, Dedup, Audit, Cost, And Recovery Prerequisites

Future implementation must define these prerequisites before adding write paths or autonomous loops:

- idempotency key for repeated operator actions
- dedup logic for repeated notifications and lesson candidates
- audit log for operator commands, owner signoff, Codex requests, and stop states
- cost ledger for AI/Codex requests
- daily request cap
- rate limiting for Discord commands and GitHub actions
- recovery playbooks for stale state, push verification failure, permission failure, and conflicting PR state
- health checks for webhook delivery, GitHub API access, AI Review Gate artifact access, and post-merge artifact access

This PR documents those prerequisites only. It does not implement storage, ledgers, health checks, or recovery automation.

## Security Risks and Mitigations

### Discord Command Injection

Risk: Discord command text could be treated as executable instructions.

Mitigation: Treat Discord input as untrusted text. Do not pass it to shell commands. Convert it into structured GitHub Issue fields or summaries only.

### GitHub Token Over-Permission

Risk: A bot token with broad write permissions could bypass intended policy.

Mitigation: Start with notification-only. Consider Issues write before any PR or contents write permission. Avoid `contents: write`, `pull-requests: write`, `actions: write`, and `administration` in v1.

### Prompt Injection

Risk: Issue bodies, PR comments, or diffs could instruct AI agents to ignore repository policy.

Mitigation: Treat all user/PR text as untrusted. `AGENTS.md`, `docs/PR_REVIEW_PLAYBOOK.md`, Issue Scope, Non-goals, and Allowed files remain higher-priority operating context.

### `@codex fix` Infinite Loop

Risk: Automated fix requests could repeat indefinitely.

Mitigation: Enforce max fix attempts, same failure repeat caps, AI commit caps, task age caps, daily Codex request caps, and `CODEX_PUSH_VERIFYING` before checks.

### Scope Creep

Risk: The bridge could turn a small task into broader implementation.

Mitigation: Require Scope, Non-goals, Allowed files / layers, and out-of-scope handling in the GitHub Issue task contract.

### Live Trading Boundary Bypass

Risk: Operator commands could accidentally enable live trading paths.

Mitigation: Treat live trading enablement, exchange credentials, risk cap increase, and model live promotion as hard stop conditions. Discord commands cannot approve them.

### Secret Exposure

Risk: Discord or GitHub summaries could echo secrets or secret-like values.

Mitigation: Do not print raw PR bodies, raw labels, raw file paths, diffs, credentials, account ids, wallet addresses, environment values, or raw exchange payloads in Discord summaries.

### Cost Runaway

Risk: Repeated AI requests could exceed cost expectations.

Mitigation: Use daily request limits, max open AI-managed PR limits, task age limits, rate limits, cost ledger, and owner-configured budget stops.

### AI-to-AI False Confidence

Risk: AI reviewer, fixer, and summarizer could reinforce a wrong assumption.

Mitigation: Keep CI, AI Review Gate, branch protection, conditional auto-merge, source-of-truth verification, loop guards, and owner hard prohibitions independent.

### Stale Projection Acting As Truth

Risk: Discord could show an outdated state that operators mistake for current truth.

Mitigation: Treat Discord as projection only. Reverify GitHub source-of-truth before every future action.

## Owner Decision Points Requiring OWNER_DECISION_REQUIRED

- Discord webhook URL 저장/회전 방식
- owner signoff 승인자 목록
- audit log 저장 위치
- idempotency/dedup ledger 저장 위치
- `@codex fix` 자동 호출 권한
- review-thread resolve 권한
- GraphQL `resolveReviewThread` 자동화 허용 여부
- daily Codex request cap
- Discord command approver list
- auto-merge blocked timeout threshold
- `@codex fix` branch-push behavior in this repository
- required permission for automated `@codex fix` comments
- Discord hosting and token storage model, if implementation is approved later

## Future Implementation Validation

Any future implementation PR must verify:

- no PR head code checkout/build/run/install/import
- no branch protection bypass
- no direct merge from Discord
- no live trading enablement path
- no exchange credential path
- no risk cap increase path
- no model live promotion path
- no raw PR body, labels, file paths, diffs, review comments, or secret-like values in Discord output
- source-of-truth re-verification before any action
- Codex push verification before checks or auto-merge eligibility
- permissions stay within the approved rollout level
