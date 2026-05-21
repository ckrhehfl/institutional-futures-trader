# Discord Operator Bridge

이 문서는 Discord 기반 AI PM Operator Bridge의 설계 경계를 정의합니다. Discord bot, GitHub Actions workflow, OpenAI API automation, GitHub App, webhook server, command handler, token handling code를 구현하지 않습니다.

## Purpose

Discord Operator Bridge의 목적은 Discord를 operator console로 사용해 사람이 반복 지시를 덜 하면서도 GitHub와 Codex 기반 작업 루프를 안전하게 조율하는 것입니다.

- Discord는 operator console입니다.
- GitHub Issues, pull requests, review comments, labels, checks가 source of truth입니다.
- Codex Cloud/GitHub integration은 planning, implementation, review, fix loop의 worker입니다.
- CI, AI Review Gate, branch protection, conditional auto-merge는 hard gates입니다.

Discord와 PM Orchestrator는 직접 code edit, branch push, merge, live trading enablement를 수행하지 않습니다.

## Non-Goals

- Discord bot 구현 금지
- GitHub Actions workflow 구현 금지
- OpenAI API automation 추가 금지
- Codex GitHub Action 추가 금지
- GitHub App 구현 금지
- Discord에서 직접 code 수정 금지
- Discord에서 직접 merge 금지
- v1에서 `contents: write`, `pull-requests: write`, `actions: write`, `administration` 권한 사용 금지
- branch protection, AI Review Gate, auto-merge workflow, model routing 수정 금지
- live trading, exchange credentials, risk cap increase, model live promotion 자동화 금지
- OMS, Risk runtime, BingX REST/WebSocket, strategy, ML, trading engine, live trading 구현 금지

## Relationship to AI Operator Loop

`docs/AI_OPERATOR_LOOP.md`가 상위 운영 원칙입니다. Discord Operator Bridge는 그 원칙을 Discord entrypoint에 적용하는 하위 설계입니다.

- 사람은 code quality reviewer가 아닙니다.
- 사람은 cost limit, direction, hard prohibitions, summary confirmation, anomaly checks의 owner입니다.
- AI/Codex, deterministic checks, CI, AI Review Gate, policy gates가 technical review와 merge readiness를 가능한 한 많이 담당합니다.
- 사람이 Discord에서 내리는 명령은 scope, cost, prohibition, escalation에 관한 operator action이어야 합니다.

## Command Catalog

### `/pm start`

GitHub Issue task contract 생성을 시작합니다.

- Required input: task summary, Scope, Non-goals, Allowed files / layers, Validation plan, Risk boundary, Owner decision points
- Output: GitHub Issue URL 또는 생성 실패 summary
- Discord-2 이전 단계에서는 설계 후보일 뿐이며 실제 Issue 생성은 구현하지 않습니다.
- Codex task 시작 방식은 확인 필요입니다.

### `/pm status`

AI-managed task 또는 PR의 현재 상태를 요약합니다.

- Shows: state, GitHub Issue/PR URL, checks, AI Review Gate verdict, labels, blocker summary, last activity age
- Does not show: raw secrets, raw PR body, raw untrusted diff text
- Does not change: PR, branch, labels, comments, merge state

### `/pm pause`

특정 task의 AI fix loop와 watcher action을 멈춥니다.

- Allows: read-only status updates
- Blocks: new `@codex fix` requests, new automation actions
- Does not disable: CI, AI Review Gate, branch protection

### `/pm resume`

pause된 task를 다시 진행 후보로 만듭니다.

- Before resume, re-check stop conditions.
- Do not resume if a hard prohibition, owner decision, cost stop, or live boundary stop is active.

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

- Add this design document only.
- No Discord bot, workflow, token, webhook, server, or API automation.

### Discord-1: Notification-Only

- Discord receives summaries of GitHub Issue/PR state.
- Read-only permissions only.
- No issue creation, PR comments, fixes, merges, or label writes.

### Discord-2: `/pm start` Creates GitHub Issue

- `/pm start` may create a GitHub Issue using the repository task contract.
- GitHub Issues write may be considered.
- The Issue remains the source of truth.
- Starting Codex work from the Issue is confirmation needed.

### Discord-3: PR Watcher / Babysitter

- Watch PR metadata, checks, AI Review Gate result, labels, review comments, and owner commands.
- Suggest or request in-scope `@codex fix` actions only after loop guard checks.
- `@codex fix` branch-push behavior in this repository is confirmation needed.

### Discord-4: Auto-Merge Status Tracking

- Track existing conditional auto-merge eligibility and blockers.
- Discord does not directly merge.
- PM Orchestrator does not directly merge.

### Discord-5: Advanced Expansion

- Possible additions: queue view, cost dashboard, richer owner summaries, stricter escalation reports.
- Live trading automation remains prohibited.

## State Machine

Primary states:

- `IDLE`: no managed task
- `TASK_CREATED`: GitHub Issue task contract exists
- `CODEX_STARTED`: Codex work was requested
- `PR_OPENED`: pull request exists
- `REVIEWING`: review, CI, or AI Review Gate is active
- `FIXING`: in-scope fix request is active
- `WAITING_FOR_CHECKS`: waiting for CI, AI Review Gate, or branch protection
- `MERGE_READY`: required checks pass and no blocking stop condition is active
- `MERGED`: PR merged
- `LESSON_CAPTURED`: post-merge lesson capture completed or no lesson captured
- `DONE`: operator loop is complete

Stop states:

- `STOPPED_POLICY`: owner policy decision required
- `STOPPED_COST`: cost limit or cost anomaly reached
- `STOPPED_LOOP_LIMIT`: loop guard exceeded
- `STOPPED_ALLOWED_FILES`: allowed files / layers violation detected
- `STOPPED_LIVE_BOUNDARY`: live trading, credentials, risk cap, or model promotion boundary touched
- `STOPPED_CODEX_FAILED`: Codex branch push, review, or fix action failed
- `STOPPED_CONFLICT`: merge conflict or incompatible branch state detected

## PM Watcher / PR Babysitter Design

The watcher observes GitHub metadata only. It should watch:

- GitHub Issue state and task contract fields
- PR metadata and labels
- PR changed file metadata
- CI check conclusions
- AI Review Gate output
- review comments and unresolved thread counts
- owner commands
- auto-merge eligibility state

The watcher must not:

- checkout PR head code
- build PR head code
- run PR head code
- install PR dependencies
- import PR code
- execute Discord text, Issue body, PR body, comments, labels, file paths, or diffs

Discord text, GitHub Issue body, PR body, comments, labels, file names, and diffs are untrusted text data.

`@codex fix` may be considered only when all of these are true:

- the review item is `IN_SCOPE_BUG` or `IN_SCOPE_DOC_OR_TEST_FIX`
- the fix stays inside the Issue/PR Allowed files / layers
- loop guards have not been exceeded
- no stop condition is active
- no live trading, credential, risk cap, or model promotion boundary is touched

`@codex fix` branch-push behavior in this repository is confirmation needed until validated.

## Auto-Merge Boundary

- Discord never directly merges.
- PM Orchestrator never directly merges.
- Existing conditional auto-merge remains the only merge automation path.
- No `--admin`.
- No branch protection bypass.
- CI and AI Review Gate remain required checks.
- Live trading enablement is separate from main branch merge automation.

## Permission Model

- Discord-0: no permissions
- Discord-1: read-only / notification-only
- Discord-2: GitHub Issues write may be considered
- Discord-3: PR watcher should prefer read permissions
- Discord-4: auto-merge status tracking should read existing status only

v1 avoids:

- `contents: write`
- `pull-requests: write`
- `actions: write`
- `administration`
- secrets access
- branch protection changes
- repository secret reads or writes

Any write permission expansion requires an owner decision before implementation.

Required permission for automated `@codex fix` comments is confirmation needed.

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
- AI Review Gate returns `FAIL` twice
- AI Review Gate returns `NEEDS_OWNER_POLICY` once
- allowed files / layers violation
- live trading, credentials, risk cap, or model promotion detected
- unexpected workflow/security file changes
- merge conflict
- Codex branch push failure
- auto-merge blocked too long
- cost limit reached
- PR scope conflicts with Issue task contract
- `@codex fix` proposes or pushes out-of-scope changes

After a stop condition, the bridge reports a summary and waits for owner direction. It does not keep fixing.

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

Mitigation: Enforce max fix attempts, same failure repeat caps, AI commit caps, task age caps, and daily Codex request caps.

### Scope Creep

Risk: The bridge could turn a small task into broader implementation.

Mitigation: Require Scope, Non-goals, Allowed files / layers, and out-of-scope handling in the GitHub Issue task contract.

### Live Trading Boundary Bypass

Risk: Operator commands could accidentally enable live trading paths.

Mitigation: Treat live trading enablement, exchange credentials, risk cap increase, and model live promotion as hard stop conditions. Discord commands cannot approve them.

### Secret Exposure

Risk: Discord or GitHub summaries could echo secrets or secret-like values.

Mitigation: Do not print raw PR bodies, raw labels, raw file paths, diffs, credentials, account ids, wallet addresses, or environment values in Discord summaries.

### Cost Runaway

Risk: Repeated AI requests could exceed cost expectations.

Mitigation: Use daily request limits, max open AI-managed PR limits, task age limits, and owner-configured budget stops.

### AI-to-AI False Confidence

Risk: AI reviewer, fixer, and summarizer could reinforce a wrong assumption.

Mitigation: Keep CI, AI Review Gate, branch protection, conditional auto-merge, loop guards, and owner hard prohibitions independent.

## Owner Decision Points / 확인 필요

- Whether v1 starts as notification-only or Issues write
- Discord command approver list
- `max_codex_requests_per_day`
- auto-merge blocked timeout threshold
- `@codex fix` branch-push behavior in this repository
- required permission for automated `@codex fix` comments
- Discord hosting and token storage model, if implementation is approved later
- audit log retention requirements for operator commands

## Future Implementation Validation

Any future implementation PR must verify:

- no PR head code checkout/build/run/install/import
- no branch protection bypass
- no direct merge from Discord
- no live trading enablement path
- no exchange credential path
- no risk cap increase path
- no model live promotion path
- permissions stay within the approved rollout level
