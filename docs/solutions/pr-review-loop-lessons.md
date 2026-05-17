# PR Review Loop Lessons

이 문서는 PR #2 Domain Model v0, PR #3 AGENTS/roadmap, PR #4 Compound Engineering config 과정에서 확인한 review loop 교훈을 저장소 지식으로 남깁니다. 목적은 같은 범위 판단 실수와 반복 리뷰를 다음 PR에서 줄이는 것입니다.

## 1. Long Review Commit Stack

- Symptom: PR #2에서 커밋이 약 40개 가까이 쌓였고 리뷰 대응 흐름이 길어졌습니다.
- Root cause: 작은 버그 수정, scope clarification, review response가 같은 PR 안에서 계속 누적됐습니다.
- Example: Domain Model v0 PR에서 validation, invariant, metadata rule 보강 커밋이 반복적으로 추가됐습니다.
- Rule to prevent recurrence: 구현 PR은 merge 전 의미 있는 단위로 squash merge하고, PR 본문에 scope와 non-goals를 유지합니다.
- Where this rule is enforced:
  - test: 없음
  - AGENTS.md: PR scope rules
  - PR template: Scope, Non-goals, Follow-up items
  - docs: `docs/PR_REVIEW_PLAYBOOK.md`
  - playbook: Squash merge 기준
- Follow-up action: 리뷰 대응 커밋이 많아지면 merge 전 squash merge를 기본 선택지로 둡니다.

## 2. Repeated GitHub/Codex Review Calls

- Symptom: GitHub/Codex review를 반복 호출하면서 리뷰 루프가 길어졌습니다.
- Root cause: 새 리뷰를 받기 전에 남은 thread의 범위, 해결 여부, follow-up 여부를 명확히 분류하지 않았습니다.
- Example: PR #3에서 roadmap scope 문구 수정 후 새 리뷰가 다시 같은 범위 판단을 지적했습니다.
- Rule to prevent recurrence: 새 리뷰가 달리면 먼저 `docs/PR_REVIEW_PLAYBOOK.md` 기준으로 분류하고, in-scope 항목만 수정합니다.
- Where this rule is enforced:
  - test: 없음
  - AGENTS.md: review triage rule
  - PR template: Review guidance
  - docs: `docs/PR_REVIEW_PLAYBOOK.md`
  - playbook: Review comment 분류 기준
- Follow-up action: 리뷰 요청 전 unresolved thread와 allowed files를 먼저 확인합니다.

## 3. P1/P2 Is Not Automatically In Scope

- Symptom: P1/P2 리뷰를 현재 PR에서 무조건 처리해야 하는 것처럼 해석할 위험이 있었습니다.
- Root cause: severity와 PR scope를 분리하지 않았습니다.
- Example: PR #3 문서 PR에서 scaffold/runtime 구현을 암시하는 리뷰가 있을 때, 코드 구현으로 대응하면 범위가 커질 수 있었습니다.
- Rule to prevent recurrence: P1/P2라도 현재 PR scope 밖이면 owner 판단 또는 follow-up으로 분류합니다.
- Where this rule is enforced:
  - test: 없음
  - AGENTS.md: P1/P2 scope rule
  - PR template: Review guidance
  - docs: `docs/PR_REVIEW_PLAYBOOK.md`
  - playbook: OUT_OF_SCOPE_FOLLOW_UP, OWNER_DECISION_REQUIRED
- Follow-up action: 리뷰 대응 전 PR Scope, Non-goals, Allowed files를 다시 읽습니다.

## 4. Domain Model Scope vs Runtime Scope

- Symptom: Domain Model v0 범위와 adapter, OMS, Risk Engine, live trading 같은 범위 밖 구현이 섞일 위험이 있었습니다.
- Root cause: domain model, runtime path, exchange adapter의 경계가 PR마다 반복 설명되어야 했습니다.
- Example: core domain validation 리뷰 중 exchange-specific adapter 구현 요구처럼 보이는 제안이 나올 수 있었습니다.
- Rule to prevent recurrence: Domain Model v0는 exchange-independent core, validation, tests에 한정하고 runtime 구현은 follow-up PR로 분리합니다.
- Where this rule is enforced:
  - test: exchange-independence와 invariant tests
  - AGENTS.md: Architecture Rules, Hard Non-Goals
  - PR template: This PR intentionally does not implement...
  - docs: roadmap와 architecture docs
  - playbook: out-of-scope implementation handling
- Follow-up action: Domain Events v0부터도 PR마다 forbidden runtime paths를 PR template에 명시합니다.

## 5. Scaffold Can Be Mistaken For Runtime Framework

- Symptom: `pyproject.toml`, `src`, `tests` scaffold가 runtime framework로 오해될 수 있었습니다.
- Root cause: approved minimal scaffold와 event bus/runtime framework의 차이를 충분히 강조하지 않았습니다.
- Example: PR #3 roadmap에서 scaffold 완료 여부와 현재 PR non-goals가 충돌하는 것처럼 읽혔습니다.
- Rule to prevent recurrence: approved minimal scaffold는 import/test/lint 가능성만 위한 것이며 trading runtime, event bus, exchange path가 아니라고 명시합니다.
- Where this rule is enforced:
  - test: project structure tests
  - AGENTS.md: Approved Minimal Scaffold
  - PR template: Allowed files / layers
  - docs: `docs/DEVELOPMENT_ROADMAP.md`
  - playbook: documentation contradiction handling
- Follow-up action: scaffold 관련 PR은 runtime framework non-goal을 PR 본문에 반복 기재합니다.

## 6. Real Bug Reviews Need Tests

- Symptom: boolean flag validation처럼 실제 bug성 리뷰는 문구 수정만으로는 재발을 막기 어렵습니다.
- Root cause: bug fix와 regression test를 분리하거나 test-first 흐름을 놓칠 수 있었습니다.
- Example: boolean constraint flag가 bool인지 검증하는 리뷰는 domain behavior bug로 분류되어야 했습니다.
- Rule to prevent recurrence: IN_SCOPE_BUG는 실패 테스트를 먼저 추가하고 최소 구현으로 통과시킵니다.
- Where this rule is enforced:
  - test: regression tests
  - AGENTS.md: Testing Rules
  - PR template: Validation
  - docs: `docs/PR_REVIEW_PLAYBOOK.md`
  - playbook: IN_SCOPE_BUG handling
- Follow-up action: bug성 리뷰는 "test added/updated"를 PR response에 포함합니다.

## 7. Optional And Style Feedback Should Not Expand Scope

- Symptom: optional/style/follow-up 리뷰를 현재 PR에서 무리하게 고치면 PR 범위가 흐려집니다.
- Root cause: review suggestion을 merge blocker와 동일하게 취급할 수 있었습니다.
- Example: 이름, 표현, 구조 개선 정도의 리뷰가 runtime 또는 broader documentation refactor로 번질 수 있었습니다.
- Rule to prevent recurrence: OPTIONAL_OR_STYLE은 merge blocker가 아니면 보류하거나 follow-up으로 남깁니다.
- Where this rule is enforced:
  - test: 없음
  - AGENTS.md: Review Guidelines
  - PR template: Follow-up items
  - docs: `docs/PR_REVIEW_PLAYBOOK.md`
  - playbook: OPTIONAL_OR_STYLE handling
- Follow-up action: optional/style thread에는 보류 이유와 follow-up 여부를 댓글로 남깁니다.

## 8. Run Superpowers Code Review Before Merge

- Symptom: PR 생성 후에야 scope 문제나 review loop risk가 드러날 수 있었습니다.
- Root cause: PR 생성 전 또는 merge 전 dedicated code review step을 명시하지 않았습니다.
- Example: 문서 PR에서도 allowed files와 non-goals가 리뷰 기준과 맞는지 사전 점검이 필요했습니다.
- Rule to prevent recurrence: 구현 PR은 PR 생성 전 또는 merge 전에 Superpowers code review를 실행합니다.
- Where this rule is enforced:
  - test: 없음
  - AGENTS.md: PR workflow rule
  - PR template: Review guidance
  - docs: `docs/PR_REVIEW_PLAYBOOK.md`
  - playbook: Superpowers + Compound Engineering workflow
- Follow-up action: 문서-only PR은 diff scope check, 구현 PR은 code review까지 PR checklist에 적습니다.

## 9. Capture Learning After PR Close

- Symptom: 리뷰 대응에서 얻은 교훈이 다음 PR로 이어지지 않으면 같은 긴 프롬프트가 반복됩니다.
- Root cause: merge 후 learning loop가 명시적이지 않았습니다.
- Example: PR #2/#3/#4에서 scope, worktree, review classification 교훈이 대화에만 남을 수 있었습니다.
- Rule to prevent recurrence: PR 종료 후 `/ce-compound` 또는 수동 compound learning note를 실행합니다.
- Where this rule is enforced:
  - test: 없음
  - AGENTS.md: compound learning rule
  - PR template: Compound learning note
  - docs: `docs/solutions/pr-review-loop-lessons.md`
  - playbook: Compound learning loop
- Follow-up action: merge 후 반복 실수를 test, AGENTS.md, PR template, docs, playbook 중 하나에 반영했는지 기록합니다.

## 10. Keep Main History Readable

- Symptom: 리뷰 대응 커밋이 많으면 main history가 noisy해질 수 있습니다.
- Root cause: review loop가 길어진 branch를 그대로 merge할 경우 세부 대응 커밋이 모두 남습니다.
- Example: PR #2처럼 많은 리뷰 대응 커밋이 쌓이면 main에서는 하나의 Domain Model v0 변화로 읽히는 편이 낫습니다.
- Rule to prevent recurrence: 리뷰 대응 커밋이 많으면 squash merge로 main history를 정리합니다.
- Where this rule is enforced:
  - test: 없음
  - AGENTS.md: PR Scope Rules
  - PR template: Follow-up items
  - docs: `docs/PR_REVIEW_PLAYBOOK.md`
  - playbook: Squash merge 기준
- Follow-up action: merge 전 "squash recommended?"를 PR 마무리 체크에 포함합니다.
