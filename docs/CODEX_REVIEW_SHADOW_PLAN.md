# Codex Review Shadow Plan

이 문서는 Codex Review report-only / shadow-review 실험을 위한 계약 문서다. 목적은 Codex Review를 required gate로 즉시 승격하지 않고, AI Review Gate와의 차이를 관찰할 수 있는 기준을 owner가 검토할 수 있게 하는 것이다.

이 문서는 구현이 아니다. 이 문서는 Codex Review automation, GitHub write permission, workflow, branch protection, AI Review Gate 변경, Discord-1a, OpenAI API automation, live trading 관련 변경을 승인하지 않는다. Owner approval 전에는 자동화 구현을 시작하지 않는다.

## 요약

Codex Review는 현재 advisory review다. AI Review Gate는 현재 required check다. 이 문서는 Codex Review를 required gate로 만들지 않고, report-only / shadow-review로 관찰할 때 어떤 정보를 비교하고 어떤 경계 안에서 운영할지 정리한다.

Shadow-review의 목적은 merge를 막는 것이 아니라 evidence를 수집하는 것이다. Codex Review finding은 owner triage 전까지 advisory signal이며, branch protection, auto-merge eligibility, CI, AI Review Gate verdict를 대체하지 않는다.

## 현재 상태

| 항목 | 현재 상태 | 운영 경계 |
| --- | --- | --- |
| AI Review Gate | required check | `PASS`가 아니면 branch protection에서 merge를 막을 수 있다. |
| Codex Review | advisory review | `@codex review`로 PR review/comment를 남길 수 있지만 required check가 아니다. |
| CI | deterministic required check | test, lint, format, safety 검증을 수행한다. |
| Conditional auto-merge | control loop | branch protection을 우회하지 않고 GitHub auto-merge를 enable/disable한다. |

Codex Review는 merge 후에도 comment 또는 review를 남길 수 있다. 따라서 merged PR에서 Codex Review를 반복 호출하면 post-merge follow-up loop가 생길 수 있다.

## 문제 정의

Codex Review가 AI Review Gate보다 더 잘 잡는 항목이 있을 수 있다. 예를 들어 docs-only prose consistency, review-loop risk, explanation clarity 같은 advisory finding은 PR 흐름에서 유용할 수 있다.

하지만 Codex Review output은 PR review/comment 형태다. 이 output을 structured required gate로 바로 쓰기는 어렵고, finding이 merge blocker인지 advisory suggestion인지 구분해야 한다. Advisory finding을 blocker처럼 오해하면 owner role, branch protection, AI Review Gate, auto-merge 경계가 흐려질 수 있다.

## 목표

- Codex Review를 report-only / shadow-review로 관찰한다.
- AI Review Gate verdict와 Codex Review finding의 차이를 기록한다.
- False positive와 false negative를 비교한다.
- Required gate 승격 전 evidence를 수집한다.
- Merge blocking, branch protection, auto-merge eligibility에는 영향을 주지 않는다.
- Owner triage 없이 advisory finding을 blocker로 취급하지 않는다.

## Non-goals

- Codex Review required gate 구현 없음.
- GitHub Actions workflow 구현 없음.
- GitHub write permission 추가 없음.
- GitHub API 수집 자동화 구현 없음.
- `@codex fix` 자동화 없음.
- review-thread resolve 자동화 없음.
- workflow rerun 자동화 없음.
- AI Review Gate workflow, prompt, model routing 변경 없음.
- Branch protection 또는 auto-merge workflow 변경 없음.
- Discord-1a 또는 OpenAI API automation 구현 없음.
- live trading, exchange credentials, risk cap increase, model live promotion 연결 없음.

## Shadow-review 기본 원칙

- No-write: shadow-review는 GitHub state를 변경하지 않는다.
- No-required-gate: Codex Review finding은 required check가 아니다.
- No-merge-blocking: shadow-review 결과는 branch protection이나 auto-merge eligibility에 직접 연결되지 않는다.
- No-auto-fix: `@codex fix` 자동 호출을 하지 않는다.
- No-review-thread-resolve: review-thread resolve를 자동화하지 않는다.
- No-raw-sensitive-data-storage: 별도 owner-approved retention policy 없이 raw sensitive data를 저장하지 않는다.
- Owner triage required: finding의 의미는 owner triage 후에만 판단한다.

## Data to collect

Shadow-review에서 수동으로 기록할 최소 후보 데이터는 다음과 같다.

| 필드 | 설명 |
| --- | --- |
| PR number | 대상 PR 번호 |
| PR type | `docs-only`, `workflow-policy`, `source-test` 중 하나 |
| changed-file risk tier | low, default, high 같은 기존 risk tier 요약 |
| AI Review Gate verdict | `PASS`, `FAIL`, `NEEDS_OWNER_POLICY` |
| AI Review Gate classification | gate finding의 classification |
| Codex Review finding 여부 | finding이 있었는지 여부 |
| Codex Review finding category | docs consistency, safety, scope, optional/style 등 owner가 정한 category |
| finding timing | merge 전 issue인지 post-merge advisory issue인지 |
| owner triage result | 아래 triage 값 중 하나 |
| follow-up PR 발생 여부 | finding 때문에 follow-up PR이 생겼는지 여부 |
| same issue 반복 여부 | 같은 issue가 반복되는지 여부 |

Owner triage result 후보:

- true positive
- false positive
- AI Review Gate false negative
- Codex Review false negative
- out-of-scope follow-up
- owner policy decision

## Data not to store

별도 owner-approved retention policy 전에는 다음 데이터를 저장하지 않는다.

- raw PR body
- raw diff
- raw review comments
- raw labels
- secret-like values
- account IDs
- wallet addresses
- env values
- webhook URLs
- exchange payloads

필요한 경우에도 raw text 대신 PR number, source timestamp, short SHA, finding category, redacted summary 같은 최소 metadata를 우선 사용한다.

## Manual sampling plan

초기 shadow-review는 자동화 없이 owner가 선택한 PR에서만 수동 샘플링한다.

- Merged PR에 습관적으로 `@codex review`를 호출하지 않는다.
- 사후 감사 목적이 있을 때만 `@codex review`를 호출한다.
- Codex Review 결과는 blocker가 아니라 advisory로 취급한다.
- Follow-up PR이 필요하면 기존 merged PR을 수정하지 않고 새 PR로 처리한다.
- 동일 유형 finding이 반복되면 AI Review Gate prompt, checklist, 또는 운영 문서 보강 후보로 기록하되, 즉시 자동화하지 않는다.

## Report-only / shadow-review future options

| Option | 설명 | 현재 판단 |
| --- | --- | --- |
| Option A | 수동 기록만 유지 | 가장 안전한 기본값이다. |
| Option B | docs-only tracking table 또는 issue template 검토 | owner가 기록 위치를 정한 뒤 검토할 수 있다. |
| Option C | workflow 기반 structured comparison | future `OWNER_DECISION_REQUIRED`다. |
| Option D | required gate 승격 | 장기 decision이며 충분한 evidence 전에는 금지한다. |

## Risk / failure modes

- Noisy review: Codex Review가 optional/style finding을 많이 만들 수 있다.
- Duplicate follow-up loop: merged PR 사후 리뷰가 같은 종류의 docs-only follow-up PR을 반복 생성할 수 있다.
- Advisory/blocker 혼동: advisory finding을 required blocker처럼 오해할 수 있다.
- Permission creep: 기록 자동화가 GitHub write permission 확장으로 이어질 수 있다.
- Output 구조 불안정: PR review/comment 형태가 structured comparison에 부족할 수 있다.
- False confidence: AI Review Gate와 Codex Review가 모두 조용하면 안전하다고 오해할 수 있다.
- Scope creep into `@codex fix`: shadow-review가 자동 fix loop로 확장될 수 있다.
- Review-thread resolve 확장 위험: cleanup 편의가 merge gate에 영향을 주는 권한 surface로 커질 수 있다.

## Stop conditions

다음 상황에서는 shadow-review 실험을 멈추고 owner decision으로 남긴다.

- Codex Review를 required gate로 바로 연결해야 하는 경우.
- GitHub write permission이 필요한 경우.
- workflow rerun, review-thread resolve, `@codex fix` 자동화가 필요한 경우.
- raw PR body, raw diff, raw comment, secret-like text 저장이 필요한 경우.
- branch protection 또는 auto-merge policy 변경이 필요한 경우.
- AI Review Gate prompt 또는 workflow 변경이 필요한 경우.
- Discord-1a 또는 OpenAI API automation과 연결되는 경우.
- live trading, credentials, risk cap, model promotion과 연결되는 경우.
- owner triage 기준 없이 finding을 blocker로 처리해야 하는 경우.

## Owner decisions required

이 문서는 아래 항목을 승인하지 않는다. 모두 `OWNER_DECISION_REQUIRED`로 남긴다.

- shadow-review 기간
- 샘플 PR 수
- PR type 분류 기준
- false positive / false negative 기록 위치
- raw review data retention 여부
- Codex Review 결과 triage 담당자
- GitHub API 기반 수집 허용 여부
- workflow 기반 comparison 허용 여부
- report-only 실험 중단 조건
- required gate 승격 최소 evidence 기준

## 다음 단계

1. 이 문서를 merge한다.
2. Post-merge ce-compound로 새 durable lesson 여부를 판단한다.
3. Owner가 수동 sampling 기간과 기록 방식을 결정한다.
4. 선택된 PR에서만 Codex Review를 advisory로 샘플링한다.
5. 충분한 evidence가 쌓이기 전에는 Codex Review automation, workflow comparison, required gate 승격을 구현하지 않는다.

Owner approval 전에는 자동화 구현을 시작하지 않는다.
