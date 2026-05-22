# Discord-1b Source-of-Truth Summarizer

## 1. Purpose

이 문서는 Discord-1b `read-only source-of-truth summarizer`의 docs-only boundary를 고정합니다. Discord-1b는 GitHub source-of-truth 상태를 Discord로 redacted/read-only projection하는 규약이며, command execution 또는 control-plane write path를 여는 기능이 아닙니다.

핵심 원칙은 다음과 같습니다.

- Discord는 source of truth가 아닙니다.
- GitHub PR/check/artifact/docs가 source of truth입니다.
- Discord는 source-of-truth 검증 결과를 축약한 projection입니다.

## 2. Scope

- Discord-1b의 문서 경계, 용어, revalidation 순서, redaction 규칙을 정의합니다.
- Discord-1a notification-only 경계와의 관계를 명확히 분리합니다.
- Discord 요약이 owner sign-off, merge approval, policy approval을 대체하지 않음을 명시합니다.

## 3. Non-goals

- Discord bot 구현
- Discord slash command 구현
- `/pm status`, `/pm summary`, `/pm start` 구현
- GitHub write permission 추가
- issue/PR comment 작성, label 변경, branch push automation
- workflow rerun, review-thread resolve, auto-merge control, `@codex fix` 자동화
- lesson PR 자동 생성
- OpenAI API coding bot 또는 GitHub App 구현
- workflow 구현 또는 수정
- Backtest runtime/contract implementation
- source/test/runtime/trading/OMS/Risk/BingX/strategy/ML/live trading 변경

## 4. Source-of-truth hierarchy

1. GitHub PR metadata, check runs, workflow run metadata, artifacts metadata
2. Repository policy docs (`AGENTS.md`, roadmap/policy docs)
3. Discord redacted summary message

Discord message는 운영 편의용 신호이며 승인 근거가 아닙니다. source-of-truth와 불일치 시 Discord 요약은 즉시 보조 신호로 격하합니다.

## 5. Documentation source-of-truth map

- `AGENTS.md` = project constitution / hard non-goals / architecture rules / documentation rules
- `docs/DEVELOPMENT_ROADMAP.md` = current implementation step / roadmap source of truth
- `docs/AUTOMATION_STATUS.md` = automation implemented/manual/advisory/designed/prohibited status map
- `docs/PR_REVIEW_PLAYBOOK.md` = review comment classification and handling rules
- `docs/DISCORD_OPERATOR_BRIDGE.md` = Discord operator bridge high-level design
- `docs/DISCORD_1A_OWNER_DECISIONS.md` = Discord-1a owner decisions only
- `docs/DISCORD_1A_NOTIFICATION_ONLY_PLAN.md` = Discord-1a notification-only planning boundary
- `docs/DISCORD_1B_SOURCE_OF_TRUTH_SUMMARIZER.md` = Discord-1b read-only summarizer boundary
- `docs/solutions/**` = durable lessons only, not general planning docs
- `docs/LIVE_TRADING_GATE.md` = live trading hard gate
- `docs/AI_REVIEW_GATE.md` and `docs/AUTO_MERGE_POLICY.md` = AI Review Gate / Auto Merge policy source docs

## 6. Documentation impact classifier

- project constitution impact -> `AGENTS.md`
- roadmap/current step impact -> `docs/DEVELOPMENT_ROADMAP.md`
- automation state impact -> `docs/AUTOMATION_STATUS.md`
- Discord operator policy impact -> `docs/DISCORD_*`
- review/triage policy impact -> `docs/PR_REVIEW_PLAYBOOK.md`
- durable repeated lesson impact -> `docs/solutions/**`
- live boundary impact -> `docs/LIVE_TRADING_GATE.md`
- AI Review Gate / Auto Merge policy impact -> `docs/AI_REVIEW_GATE.md`, `docs/AUTO_MERGE_POLICY.md`

분류 원칙:

- 영향 범위가 확실하면 해당 문서 업데이트 필요성을 제안합니다.
- 영향 범위가 애매하면 자동 수정하지 않고 `OWNER_DECISION_REQUIRED`로 멈춥니다.
- classifier는 문서 영향과 owner decision 필요 여부를 분류할 뿐, 위험한 결정을 승인하지 않습니다.

## 7. GitHub source revalidation order

Discord 요약을 보내기 전, 다음 순서로 GitHub source를 재검증합니다.

1. PR number 존재 여부
2. PR 존재 여부 (deleted/invalid 방지)
3. same-repository 여부 (external/fork 분리)
4. base branch가 `main`인지
5. workflow event head SHA와 현재 PR head SHA 일치 여부
6. check status/conclusion의 최신성
7. artifact availability와 접근 가능성
8. AI Review Gate verdict category의 안전한 획득 가능성

위 단계 중 하나라도 실패하면 send 대신 suppress 또는 `CHECK_SOURCE_OF_TRUTH` 경로를 사용합니다.

## 8. Redaction boundary

허용: 상태 판단에 필요한 최소 메타데이터만 허용합니다.

금지: 원문 텍스트/원본 payload/secret-like 값을 Discord에 그대로 노출하지 않습니다.

- raw PR text, raw review text, raw artifact contents, raw Codex output 금지
- secret/token/API key/account identifier/wallet/environment value/webhook URL 금지
- raw exchange payload 및 trading 민감정보 금지

## 9. Allowed Discord output fields

- repository
- event type
- workflow name
- check status
- check conclusion
- source revalidation status
- workflow run id
- owner action category from fixed allowlist
- pr_number
- pr_state
- base_branch
- short_head_sha
- pr_url
- ai_review_gate_verdict_category (safely available일 때만)
- documentation impact category summary (redacted path-category 기반일 때만)

## 10. Forbidden Discord output fields

- raw PR title
- raw PR body
- raw labels
- raw diff
- raw comments
- raw review text
- raw Codex output
- raw artifact contents
- raw file contents
- unnecessary raw file path list
- secrets, tokens, API keys
- account identifiers
- wallet addresses
- environment values
- Discord webhook URL
- raw exchange payload
- trading signal, order, position, credential data

## 11. Stale-state and mismatch handling

다음은 suppress 또는 `CHECK_SOURCE_OF_TRUTH`로 분류합니다.

- missing PR number
- missing PR
- non-main base
- external/fork PR
- stale head SHA
- missing artifact
- inconsistent check state

stale Discord message는 후속 action 승인 근거가 아닙니다. source-of-truth mismatch가 있으면 write/control action 없이 중단합니다.

## 12. AI Review Gate verdict handling

- `PASS`: 요약 가능하지만 merge approval로 표현하지 않습니다.
- `FAIL`: fix loop trigger가 아니라 `STOPPED_POLICY` 또는 `CHECK_SOURCE_OF_TRUTH`로 표현합니다.
- `NEEDS_OWNER_POLICY`: `OWNER_DECISION_REQUIRED`로 표현합니다.

Discord summary는 owner sign-off를 대체하지 않습니다.

## 13. Post-merge artifact boundary

- post-merge artifact는 상태 카테고리 요약만 허용합니다.
- raw artifact 다운로드 결과나 원문은 Discord에 전달하지 않습니다.
- post-merge 후속 action은 owner/operator가 GitHub source-of-truth를 직접 재확인한 뒤 결정합니다.

## 14. Relationship to Discord-1a

- Discord-1b는 Discord-1a의 대체가 아닙니다.
- Discord-1a는 notification-only workflow 구현 경계입니다.
- Discord-1b는 source-of-truth summarization 규약 문서이며 command path가 아닙니다.
- Discord-1b는 slash command 설계/구현을 포함하지 않습니다.

## 15. Future implementation shape

구현은 본 문서 범위 밖이며 후속 owner decision 이후 별도 PR에서 검토합니다.

선택지:

- separate workflow로 독립 구현
- Discord-1a의 future extension으로 제한적 확장

어느 경로든 공통 제약은 동일합니다.

- read-only
- redacted projection only
- no GitHub write/control path
- no command handler

## 16. Owner decisions required

- Discord-1b를 separate workflow로 구현할지, Discord-1a extension으로 구현할지
- 허용 output field allowlist의 최종 고정 범위
- `documentation impact category summary` 노출 granularity
- stale-state 임계치와 suppress taxonomy 운영 정책
- AI Review Gate verdict unavailable 시 fallback 표현 정책

## 17. Stop conditions

다음 조건 중 하나라도 발생하면 구현 논의를 멈추고 owner 재승인이 필요합니다.

- write/control path 요구가 등장하는 경우
- raw text/payload 노출 요구가 등장하는 경우
- non-main/fork/stale 검증 생략 요구가 등장하는 경우
- Discord summary를 merge/policy approval 대체로 쓰려는 요구가 등장하는 경우
- Backtest 또는 trading runtime 범위와 결합하려는 요구가 등장하는 경우

## 18. Validation plan

문서 PR 기준 검증:

- changed files가 Allowed files와 정확히 일치하는지 확인
- 금지 경로(`.github/**`, `src/**`, `tests/**`) 변경 없음 확인
- `git diff --check`로 문법/whitespace 문제 확인
- `rg` 기반 금지/민감 키워드 노출 sanity check 수행
- `pre-commit run --all-files --show-diff-on-failure` 실행 가능 시 수행
- 실행 불가 시 환경 제한으로 분리 보고
