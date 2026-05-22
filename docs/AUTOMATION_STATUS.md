# Automation Status

이 문서는 현재 저장소의 automation 상태를 한눈에 보기 위한 status map입니다. 새 정책을 승인하거나 새 automation을 구현하는 문서가 아닙니다. 구현 상태, 수동 단계, advisory 기능, 설계만 된 영역, 금지 또는 봉인된 영역을 구분해 다음 작업 전 혼란을 줄이는 것이 목적입니다.

## 요약

이 저장소는 아직 자동매매 봇을 구현하는 단계가 아닙니다. 현재 목표는 AI/Codex가 안전하게 확장할 수 있는 core contract, 검증 루프, automation infrastructure를 먼저 만드는 것입니다.

main branch merge automation과 live trading enablement는 분리되어 있습니다. `main`에 merge된다는 사실은 live trading, exchange credentials, risk cap increase, model live promotion을 승인하지 않습니다.

사람은 기본 code quality reviewer가 아닙니다. 사람의 역할은 비용 한도, 큰 방향, hard prohibition, owner sign-off, 요약 확인, 이상 징후 확인에 가깝습니다. 코드 품질과 merge readiness는 CI, AI Review Gate, deterministic checks, policy gates, branch protection, conditional auto-merge가 담당합니다.

## 상태 분류표

| Label | 의미 |
| --- | --- |
| `IMPLEMENTED` | 저장소에 구현되어 있고 현재 운영 흐름에 포함된 상태입니다. |
| `MANUAL` | 사람이 명시적으로 실행하거나 확인해야 하는 상태입니다. |
| `ADVISORY` | 참고 신호입니다. 현재 required gate나 merge blocker가 아닙니다. |
| `DESIGNED_ONLY` | 문서 설계는 있지만 구현되지 않은 상태입니다. |
| `OWNER_DECISION_REQUIRED` | 진행 전에 owner가 policy, permission, cost, risk, scope를 결정해야 하는 상태입니다. |
| `PROHIBITED` | 현재 단계에서 금지된 상태입니다. |
| `SEALED` | 별도 hard gate 통과 전까지 봉인된 상태입니다. |

## 구현 완료된 자동화

| 항목 | 상태 | 역할 | 현재 경계 |
| --- | --- | --- | --- |
| CI required check | `IMPLEMENTED` | deterministic test/lint/format/safety 검증을 수행합니다. | GitHub branch protection의 required check입니다. |
| AI Review Gate required check | `IMPLEMENTED` | PR diff와 trusted context를 기반으로 policy/scope/security review를 수행합니다. | `PASS`만 merge 가능하게 하고, `FAIL` 또는 `NEEDS_OWNER_POLICY`는 merge를 막습니다. |
| AI Review Gate deterministic model routing | `IMPLEMENTED` | changed files, labels, metadata로 risk tier와 model/effort를 결정합니다. | AI가 임의로 model을 고르지 않습니다. high-risk fallback은 조용히 낮은 model로 내려가지 않습니다. |
| Conditional auto-merge | `IMPLEMENTED` | eligible same-repository PR에 GitHub auto-merge를 enable합니다. | branch protection을 우회하지 않고, `--admin`을 쓰지 않습니다. |
| Auto-merge settling guard | `IMPLEMENTED` | PR 생성 직후나 최신 head update 직후 auto-merge가 너무 빨리 armed 되는 것을 줄입니다. | event-only workflow 한계를 문서화했고, AI Review Gate를 대체하지 않습니다. |
| Auto-merge close guard | `IMPLEMENTED` | PR #35에서 `closed` event를 처리해 closed PR의 stale GitHub auto-merge request를 disable할 수 있게 했습니다. | 사용자가 PR을 close하면 auto-merge intent 취소로 취급합니다. |
| GitHub Issue / PR templates | `IMPLEMENTED` | Scope, Non-goals, Allowed files, Validation plan, Risk boundary를 task contract로 강제합니다. | blank issue는 비활성화되어 있습니다. |
| Post-merge lesson capture workflow | `IMPLEMENTED` | merged PR 이후 lesson candidate report를 job summary와 artifact로 남깁니다. | OpenAI API를 쓰지 않고, comments/issues/commits/PR을 만들지 않습니다. |
| Discord-1a notification workflow | `IMPLEMENTED` | GitHub PR/check/artifact 상태를 Discord로 보내는 redacted/read-only notification-only workflow입니다. | GitHub Actions-only, read-only, no checkout, no dependency install, no PR head code execution, no GitHub write permission, no Codex automation, no review-thread resolve, no auto-merge control입니다. Workflow run당 최대 1개의 redacted Discord message만 보냅니다. |
| Branch protection / required checks | `IMPLEMENTED` | CI와 AI Review Gate를 merge gate로 사용합니다. | repo setting의 source of truth는 GitHub입니다. 코드로 branch protection을 변경하지 않습니다. |
| Docs-only learning note follow-up loop | `IMPLEMENTED` | ce-compound 결과가 있으면 Codex가 docs-only PR을 만들 수 있습니다. | 자동 생성이 아니라 operator가 요청한 follow-up입니다. |

## 수동 또는 반자동 단계

| 항목 | 상태 | 현재 운영 방식 |
| --- | --- | --- |
| Post-merge ce-compound | `MANUAL` | merge 후 사람이 요청하거나 판단해 실행합니다. |
| Learning note docs-only PR | `MANUAL` | learning note가 생기면 Codex가 PR을 만들 수 있지만, owner가 흐름을 확인합니다. |
| Owner sign-off | `MANUAL` | AI가 대신 작성하면 안 됩니다. owner가 PR body/comment에 직접 남겨야 합니다. |
| AI Review Gate failure triage | `MANUAL` | classification이 `IN_SCOPE_DOC_OR_TEST_FIX`인지 `OWNER_DECISION_REQUIRED`인지 사람이 확인해야 하는 경우가 있습니다. |
| Merged PR `@codex review` | `MANUAL` | 사후 감사가 필요할 때만 호출합니다. 습관적으로 호출하면 follow-up loop가 생길 수 있습니다. |
| Codex push verification | `MANUAL` | Codex가 commit했다고 말해도 PR branch, remote head SHA, commit list로 push 여부를 확인합니다. |
| Discord-1a secret and smoke validation | `MANUAL` | owner가 `DISCORD_1A_WEBHOOK_URL` repository secret을 직접 관리하고, default-branch `workflow_dispatch` dry-run과 redacted smoke test 결과를 확인합니다. |

## Advisory 기능

| 항목 | 상태 | 설명 |
| --- | --- | --- |
| Codex GitHub Review | `ADVISORY` | `@codex review`는 required check가 아닙니다. |
| Codex Review output | `ADVISORY` | PR review/comment 형태로 남을 수 있고, merge 후에도 달릴 수 있습니다. |
| Codex Review vs AI Review Gate | `ADVISORY` | Codex Review는 사람이 호출하는 review 신호이고, AI Review Gate는 branch protection에 연결된 required check입니다. |
| Future report-only/shadow-review integration | `OWNER_DECISION_REQUIRED` | Codex Review를 바로 required gate로 대체하지 않습니다. 먼저 report-only 또는 shadow-review로 검토할 수 있습니다. |

현재 권장 사용법은 Codex Review를 advisory review로만 사용하는 것입니다. Required merge blocking은 CI와 AI Review Gate가 담당합니다.

## 설계만 된 것

| 항목 | 상태 | 설명 |
| --- | --- | --- |
| Discord Operator Bridge | `DESIGNED_ONLY` | Discord를 redacted/read-only projection으로 쓰는 control-plane 설계입니다. 구현되지 않았습니다. |
| Discord-1a post-MVP expansion | `OWNER_DECISION_REQUIRED` | Discord-1a notification-only MVP는 구현 및 smoke validation까지 완료되었습니다. 이후 trigger, message schema, persistence, audit, recovery 확장은 별도 owner decision이 필요합니다. |
| Discord-1b source-of-truth summarizer | `DESIGNED_ONLY` | 문서 경계만 정의되었고 구현되지 않았습니다. read-only/redacted projection 원칙을 유지하며 workflow/write/control path를 열지 않습니다. |
| Discord-1c/2a/2b/3a/3b/3c/4a/4b/5 rollout | `DESIGNED_ONLY` | rollout 단계만 문서화되어 있습니다. Discord-1a MVP 완료나 Discord-1b 문서화가 slash command, watcher, fixer, resolver, dashboard 구현 승인을 의미하지 않습니다. |
| PR watcher / babysitter | `DESIGNED_ONLY` | read-only watcher와 guarded fix loop 후보입니다. 구현되지 않았습니다. |
| Post-merge babysitter | `DESIGNED_ONLY` | lesson capture handoff 후보입니다. 구현되지 않았습니다. |
| Automatic lesson PR creation | `DESIGNED_ONLY` | 현재는 자동 생성하지 않습니다. |
| Automatic `@codex fix` | `DESIGNED_ONLY` | 자동 호출은 허용되지 않았습니다. |
| Automatic review-thread resolve | `DESIGNED_ONLY` | v1 금지이며 future owner-approved optional feature입니다. |
| Dashboard / queue | `DESIGNED_ONLY` | advanced dashboard/queue 후보입니다. |

## 금지 또는 봉인된 것

| 항목 | 상태 | 설명 |
| --- | --- | --- |
| Live trading | `SEALED` | `docs/LIVE_TRADING_GATE.md` 통과 전까지 봉인되어 있습니다. |
| Exchange credentials | `SEALED` | 자동화 또는 docs-only PR로 열 수 없습니다. |
| Risk cap increase | `SEALED` | 별도 policy gate 없이 변경할 수 없습니다. |
| Model live promotion | `SEALED` | main merge automation과 분리되어 있습니다. |
| BingX REST/WebSocket | `PROHIBITED` | 현재 단계에서는 구현하지 않습니다. |
| Strategy/ML/trading engine runtime | `PROHIBITED` | 현재 단계에서는 구현하지 않습니다. |
| GitHub write permission expansion without owner decision | `OWNER_DECISION_REQUIRED` | 권한 확대는 별도 owner decision이 필요합니다. |
| OpenAI API coding bot | `PROHIBITED` | 새 OpenAI API coding bot은 만들지 않습니다. |
| Discord command bot implementation | `PROHIBITED` | Discord-1a notification-only MVP와 별개로 slash command나 command bot은 구현하지 않습니다. |
| Auto-merge branch protection bypass | `PROHIBITED` | `--admin`과 branch protection bypass는 금지입니다. |
| `--admin` | `PROHIBITED` | merge automation에서 사용하지 않습니다. |

## 최근 사건과 교훈

- PR #31: committed docs에 ambiguous placeholder를 남기면 AI Review Gate가 실패할 수 있습니다. 미정 정책은 `OWNER_DECISION_REQUIRED` stop state로 표현합니다.
- PR #32/#33: docs learning note prose는 한국어로 쓰고, stable technical terms는 영어로 유지해야 합니다.
- PR #33/#35: closed PR에서 armed GitHub auto-merge request가 살아남을 수 있었습니다. PR #35에서 `closed` trigger와 close guard를 추가했습니다.
- PR #36/#37: learning note도 committed docs이므로 한국어 prose 규칙을 지켜야 합니다.
- Merged PR에 반복적으로 `@codex review`를 호출하면 post-merge follow-up loop가 생길 수 있습니다. 사후 감사 목적이 있을 때만 호출합니다.
- PR #45: Discord-1a notification-only workflow가 추가되었습니다. GitHub Actions-only, read-only, notification-only이며 checkout, dependency install, PR head code execution, GitHub write path, Codex automation을 사용하지 않습니다.
- PR #47: Discord webhook POST에 explicit `User-Agent`를 추가해 `send_discord=true` smoke test의 `failed_closed_http_error`를 해결했습니다.
- PR #48: PR #47의 `User-Agent` compatibility와 redacted smoke success lesson을 기존 workflow learning note에 반영했습니다.

## AI Review Gate vs Codex Review

| 항목 | AI Review Gate | Codex Review |
| --- | --- | --- |
| 목적 | PR merge 전에 scope, policy, security, trusted context 기준으로 required gate를 수행합니다. | 사람이 요청한 advisory review를 제공합니다. |
| 실행 시점 | PR 이벤트에서 GitHub Actions required check로 실행됩니다. | `@codex review` 호출 등 사람이 요청한 시점에 실행됩니다. merge 후에도 가능할 수 있습니다. |
| merge 차단 여부 | `PASS`가 아니면 branch protection을 통해 merge를 막습니다. | 현재 required check가 아니므로 직접 merge를 차단하지 않습니다. |
| output 형태 | GitHub Actions job summary와 JSON artifact입니다. | PR review/comment 형태입니다. |
| 장점 | deterministic routing, required check, artifact 기반 추적이 가능합니다. | 사람이 필요한 시점에 추가 관점을 요청할 수 있습니다. |
| 한계 | prompt/action/workflow 경계 안에서만 판단합니다. false positive/false negative가 있을 수 있습니다. | advisory라서 merge gate가 아니며, post-merge follow-up loop를 만들 수 있습니다. |
| 현재 권장 사용법 | required merge gate로 유지합니다. | 사후 감사나 추가 검토가 필요할 때만 수동 호출합니다. |

Codex Review를 AI Review Gate의 즉시 대체물로 취급하지 않습니다. Future work로 report-only 또는 shadow-review integration을 검토할 수 있지만, 이는 `OWNER_DECISION_REQUIRED`입니다.

## 현재 운영 규칙

- Merged PR에 `@codex review`를 습관적으로 호출하지 않습니다.
- 사후 감사가 필요할 때만 `@codex review`를 호출합니다.
- Merge 후 Codex Review가 이슈를 잡으면 기존 PR을 수정하지 않고 follow-up PR로 처리합니다.
- Close한 PR은 중복 또는 취소로 간주하고, main에 들어갔는지 확인합니다.
- Codex가 commit했다고 말해도 PR branch, remote head SHA, commit list로 push 여부를 확인합니다.
- `pre-commit: command not found` 같은 Codex task 환경 문제는 GitHub CI failure와 구분합니다.
- AI Review Gate failure는 먼저 classification을 확인합니다.
- `OWNER_DECISION_REQUIRED`는 반복 fix 대상이 아니라 stop state입니다.
- Docs-only PR도 merge되면 source of truth가 됩니다.
- Workflow/security/live-boundary 변경은 high-risk로 취급합니다.

## 다음 권장 순서

1. 이 status map에 Discord-1a notification-only MVP 완료 상태를 반영합니다.
2. Discord-1a workflow는 default branch에서만 owner-controlled smoke validation을 계속합니다.
3. Discord-1a post-MVP 확장 필요 여부를 owner가 결정합니다.
4. Discord-1b/1c/2a 이후 rollout은 별도 plan과 owner approval 전까지 구현하지 않습니다.
5. Codex Review integration은 바로 required gate가 아니라 report-only/shadow-review로만 검토합니다.
6. Live trading, exchange credentials, risk cap increase, model live promotion은 계속 `SEALED` 상태로 유지합니다.

## Owner decisions still required

다음 항목은 이 문서가 승인하지 않습니다. 모두 `OWNER_DECISION_REQUIRED`입니다.

- Discord webhook URL storage/rotation
- Discord channel access
- audit log storage
- dedup/idempotency ledger
- hosting model
- rate limits
- failure notification policy
- Codex Review automation policy
- daily Codex request cap
- automatic `@codex fix` 허용 여부
- review-thread resolve 자동화 허용 여부
- Codex Review를 report-only/shadow-review로 연결할지 여부
- Discord-1a post-MVP expansion scope and allowed files

## 이 문서의 업데이트 규칙

Automation 상태가 바뀌면 이 문서를 업데이트합니다. 단, 구현 PR과 status map PR을 섞지 않습니다.

- Workflow 변경 PR은 별도로 만듭니다.
- Status map 업데이트는 별도 docs-only PR로 유지합니다.
- Source/test/runtime/trading 구현 PR과 이 문서 업데이트를 섞지 않습니다.
- Discord-1a implementation을 이 문서 변경과 함께 승인하지 않습니다.
- Live trading, exchange credentials, risk cap increase, model live promotion은 이 문서로 열 수 없습니다.
