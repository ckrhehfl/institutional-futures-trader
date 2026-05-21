# AI Operator Loop

이 문서는 사람이 code quality reviewer나 trading architecture 세부 판단자가 되지 않도록, 기존 Codex와 GitHub-native 도구를 우선 사용하는 운영 루프를 정의합니다. 새 API bot, Discord command bot, custom GitHub fixer bot, secret-bearing automation을 추가하기 위한 문서가 아닙니다.

## Purpose

- 사람의 반복 복사/붙여넣기, 긴 지시 반복, 기술 세부 판단 부담을 줄입니다.
- Codex Cloud/Web, GitHub integration, Codex Automations, GitHub-native checks를 우선 사용합니다.
- 직접 OpenAI API 기반 bot을 새로 만들지 않습니다.
- AI 다중 검증, deterministic checks, CI, AI Review Gate, policy gate가 code quality와 merge readiness를 판단하게 합니다.

## Human Role

사람은 code quality reviewer가 아닙니다. 사람은 trading architecture의 세부 구현 판단자도 아닙니다.

사람이 담당하는 것은 다음으로 제한합니다.

- cost limit과 OpenAI/GitHub 사용량 이상 징후 확인
- product direction과 큰 작업 우선순위 확인
- hard prohibition 유지
- AI가 만든 summary와 merge risk 신호 확인
- policy conflict, live boundary 접촉, unusual automation behavior escalations 처리

## AI Roles

- Planner AI: Scope, Non-goals, Allowed files / layers, Validation plan을 작성합니다.
- Builder AI: 승인된 범위 안에서 implementation, tests, commit, PR creation을 수행합니다.
- Reviewer AI: code, policy, security boundary, scope adherence를 리뷰합니다.
- Triage AI: `docs/PR_REVIEW_PLAYBOOK.md` 기준으로 review comments를 분류합니다.
- Fixer AI: `IN_SCOPE_BUG` 또는 `IN_SCOPE_DOC_OR_TEST_FIX`만 최소 수정합니다.
- Gatekeeper: CI, AI Review Gate, branch protection, auto-merge policy가 merge eligibility를 판단합니다.
- Lesson Capture: post-merge report와 `/ce-compound`로 durable lesson 후보를 정리합니다.

## Existing Tools First

새 자동화보다 기존 도구를 먼저 사용합니다.

- Codex Cloud/Web for delegated planning, implementation, review, and fix loops
- GitHub `@codex review` / `@codex fix` style flow where available
- Codex Automations as a future PR babysitter candidate
- GitHub Copilot cloud agent as a comparison candidate only

부족한 부분을 바로 direct API bot이나 custom GitHub fixer bot으로 메우지 않습니다.

## No New API Automation By Default

- 새 OpenAI API workflow를 기본값으로 추가하지 않습니다.
- 새 secret-bearing automation을 추가하지 않습니다.
- Discord command bot을 만들지 않습니다.
- custom GitHub fixer bot을 만들지 않습니다.
- 현재 AI Review Gate API는 Codex Cloud/GitHub-native 대체가 검증될 때까지 유지합니다.
- 대체를 검토하더라도 branch protection, required checks, auditability가 유지되어야 합니다.

## PR Lifecycle

1. Issue template으로 task contract를 작성합니다.
2. Planner AI가 Scope, Non-goals, Allowed files, Validation plan을 확정합니다.
3. Builder AI가 승인된 범위 안에서 구현과 테스트를 진행합니다.
4. CI가 deterministic checks를 실행합니다.
5. AI Review Gate가 required check로 scope, policy, security boundary를 검토합니다.
6. Review Triage AI가 새 리뷰를 분류합니다.
7. Fixer AI가 in-scope 항목만 수정합니다.
8. Gatekeeper가 branch protection과 auto-merge policy 기준으로 merge eligibility를 판단합니다.
9. Post Merge Lesson Capture가 lesson candidate report를 남깁니다.
10. 필요한 경우 `/ce-compound` 또는 docs-only PR로 durable lesson을 반영합니다.

## Review Triage Loop

리뷰가 달리면 수정 전에 먼저 분류합니다.

- `IN_SCOPE_BUG`: 테스트 우선 또는 최소 수정으로 같은 PR에서 처리합니다.
- `IN_SCOPE_DOC_OR_TEST_FIX`: 현재 PR 범위 안에서 문서/테스트만 보강합니다.
- `OUT_OF_SCOPE_FOLLOW_UP`: 현재 PR을 넓히지 않고 follow-up으로 남깁니다.
- `OPTIONAL_OR_STYLE`: merge blocker가 아니면 보류합니다.
- `OWNER_DECISION_REQUIRED`: 사람이 policy/risk/prohibition 판단을 남겨야 합니다.

P1/P2라도 현재 PR scope 밖이면 바로 구현하지 않습니다.

## Auto-Merge Boundary

- Auto-merge는 branch protection을 우회하지 않습니다.
- `--admin` merge는 금지입니다.
- High-risk PR은 자동 merge 대상에서 제외될 수 있습니다.
- Auto-merge workflow는 AI Review Gate와 분리되어야 합니다.
- Main branch merge automation은 live trading enablement가 아닙니다.

## Cost Control

- 새 API automation보다 기존 Codex/GitHub-native 도구를 우선합니다.
- AI Review Gate model routing을 유지합니다.
- Low/default PR은 비용 예측 가능한 model/effort를 사용하고, high-risk PR은 더 강한 review model/effort를 사용합니다.
- 비용 이상 징후는 stop condition입니다.
- 사람이 직접 code quality를 판정하지 않고, 비용과 방향성의 owner로 남습니다.

## Hard Prohibitions

다음은 AI도 직접 실행할 수 없습니다.

- live trading enablement
- exchange credentials 추가 또는 노출
- risk cap increase
- model live promotion
- direct live order path 생성
- live order submission path 생성
- 승인되지 않은 secret-bearing automation 추가

Trusted workflow와 review gate에서는 PR head code checkout/build/run/install/import 금지 원칙을 유지합니다.

## Live Trading Boundary

`docs/LIVE_TRADING_GATE.md`는 hard gate입니다. AI Operator Loop, auto-merge, AI Review Gate, Codex Automations는 이 gate를 우회할 수 없습니다.

Live trading, exchange credentials, risk cap increase, model live promotion은 main branch merge automation과 분리된 별도 policy gate로 봉인합니다.

## Escalation / Stop Conditions

다음 상황에서는 자동 진행을 멈추고 owner 판단을 요청합니다.

- AI Review Gate verdict가 `FAIL` 또는 `NEEDS_OWNER_POLICY`
- CI failure가 current PR scope 밖 수정을 요구함
- allowed files / layers 위반
- secret, API key, account id, wallet address 감지
- live trading boundary 접촉
- cost anomaly
- AGENTS.md, PR template, PR_REVIEW_PLAYBOOK.md, roadmap 사이 policy conflict
- PR head code 실행, branch protection 우회, write permission 확장 요구

## Future Candidates

- Codex-native PR babysitter for recurring PR status, review, CI, and in-scope fix checks
- Issue Form to Codex Cloud delegation
- GitHub Copilot cloud agent comparison
- AI Review Gate API reduction or replacement after Codex/GitHub-native replacement is proven

현재 gate와 branch protection을 대체할 충분한 evidence가 생기기 전까지는 AI Review Gate를 제거하거나 약화하지 않습니다.
