# AI Review Gate Coverage Plan

이 문서는 AI Review Gate가 docs-only PR에서 놓치기 쉬운 coverage gap을 정리하고, 향후 `.github/prompts/ai-review-gate.md` 보강 전에 owner가 검토할 기준을 제공한다.

이 문서는 구현이 아니다. 이 문서는 AI Review Gate prompt 변경을 승인하지 않으며, workflow, model routing, branch protection, auto-merge, Codex Review automation, Discord-1a 구현도 승인하지 않는다. Prompt나 workflow 변경은 별도 owner approval이 있는 future PR에서만 다룬다.

## 요약

AI Review Gate는 required check로서 merge 전에 scope, safety, policy, documentation consistency를 검토한다. 최근 docs-only PR 흐름에서 placeholder와 documentation language consistency 문제가 드러났고, 일부는 AI Review Gate가 merge 전에 잡았지만 일부는 Codex Review가 merge 후 advisory review로 잡았다.

이번 문서의 목적은 다음 단계의 기준을 고정하는 것이다.

- docs-only PR도 merge되면 repository source of truth가 된다.
- 설명 prose는 한국어로 작성하고 stable technical terms는 영어로 유지한다.
- 미정 정책은 placeholder가 아니라 `OWNER_DECISION_REQUIRED` stop state로 표현한다.
- Codex Review는 advisory이며 AI Review Gate required check를 즉시 대체하지 않는다.
- Codex Review report-only 또는 shadow-review는 별도 owner decision 후에만 검토한다.

## 최근 배경

- PR #31: committed documentation 안의 ambiguous confirmation placeholder를 AI Review Gate가 잡았고, 해당 표현을 `OWNER_DECISION_REQUIRED` stop state로 수정했다.
- PR #32/#33: Codex Review가 learning note의 영어 narrative prose 문제를 merge 후에 지적했다.
- PR #36/#37: auto-merge closed PR lesson에서도 같은 Korean prose consistency 문제가 반복되었다.
- PR #38: `docs/AUTOMATION_STATUS.md`가 AI Review Gate와 Codex Review의 역할 차이, advisory/required gate 구분, post-merge review loop 위험을 정리했다.

## 현재 coverage gap

AI Review Gate는 required gate지만 prompt와 checklist에 명시되지 않은 docs consistency 문제를 놓칠 수 있다. 특히 docs-only PR은 코드 실행 경로를 바꾸지 않아 가벼워 보이지만, merge 후에는 운영 정책과 작업 절차의 source of truth가 된다.

Codex Review는 advisory signal이다. Merge 후에도 review를 남길 수 있고, 같은 종류의 post-merge follow-up PR이 반복되면 review loop가 생길 수 있다. 따라서 Codex Review 결과를 유용한 보조 신호로 쓰되, 즉시 required gate로 대체하지 않는다.

## AI Review Gate에 추가 검토해야 할 docs rules

향후 AI Review Gate prompt 보강 후보는 다음 규칙을 포함해야 한다.

- Explanation prose는 한국어로 작성한다.
- Stable technical terms는 영어로 유지할 수 있다.
- Ambiguous confirmation placeholder, `TBD`, `TODO`, `decide later` 같은 unfinished marker나 ambiguous placeholder requirement를 committed documentation에 남기지 않는다.
- Unresolved policy decision은 `OWNER_DECISION_REQUIRED`로 표현한다.
- `OWNER_DECISION_REQUIRED`는 placeholder가 아니라 명시적 stop state다.
- docs-only learning note, planning document, status map도 merge되면 committed source of truth로 취급한다.
- AI Review Gate 실패가 항상 owner sign-off 문제는 아니다. Gate JSON의 classification이 `IN_SCOPE_DOC_OR_TEST_FIX`이면 같은 PR에서 최소 문서 수정으로 처리할 수 있다.
- `NEEDS_OWNER_POLICY`와 `IN_SCOPE_DOC_OR_TEST_FIX`를 구분한다.
- Merge 후 `@codex review`는 advisory 감사 신호이며, 반복적인 post-merge follow-up loop를 만들 수 있음을 경고한다.

## AI Review Gate vs Codex Review

| 항목 | AI Review Gate | Codex Review |
| --- | --- | --- |
| 상태 | Required check | Advisory review |
| 목적 | merge 전 scope, policy, safety, documentation consistency gate | 추가 검토와 개선 제안 |
| merge 차단 | `PASS`가 아니면 branch protection에서 merge를 막을 수 있음 | 현재 required gate가 아니므로 직접 merge를 막지 않음 |
| output | GitHub Actions summary와 JSON artifact | PR review/comment |
| 장점 | deterministic routing, required check, artifact 기반 추적 | 사람이 필요할 때 추가 관점을 요청할 수 있음 |
| 한계 | prompt/checklist 밖 문제를 놓칠 수 있음 | merge 후에도 comment를 남겨 follow-up loop를 만들 수 있음 |
| 현재 권장 사용법 | required merge gate로 유지 | 사후 감사 또는 보조 review로 제한 |

Codex Review를 즉시 required gate로 대체하지 않는다. Codex Review automation 또는 required gate 승격은 future `OWNER_DECISION_REQUIRED`다.

## Future prompt update 후보

향후 owner approval이 있으면 `.github/prompts/ai-review-gate.md`에 아래 checklist bullet을 반영할 수 있다. 이 파일은 high-risk policy surface이며, 이번 PR에서는 수정하지 않는다.

Prompt 보강 후보:

- Check committed documentation for Korean explanation prose with English stable technical terms.
- Reject unfinished markers or ambiguous placeholders such as ambiguous confirmation placeholder text, `TBD`, `TODO`, and `decide later`.
- Require unresolved policy decisions to be expressed as `OWNER_DECISION_REQUIRED`.
- Treat docs-only learning notes, planning docs, and status maps as committed source of truth.
- Distinguish `IN_SCOPE_DOC_OR_TEST_FIX` from `OWNER_DECISION_REQUIRED` before recommending an owner sign-off.
- Warn when a proposed workflow depends on repeated post-merge `@codex review` follow-up loops.
- Keep Codex Review advisory unless a future owner-approved report-only/shadow-review process proves otherwise.

## Codex Review report-only/shadow-review 검토 조건

Codex Review를 바로 required gate로 연결하지 않는다. 먼저 report-only 또는 shadow-review로 검토하려면 다음 조건이 필요하다.

- Codex Review output이 비교 가능한 structured output으로 정리되어야 한다.
- AI Review Gate verdict와 Codex Review finding을 PR 유형별로 비교해야 한다.
- False positive와 false negative를 기록해야 한다.
- docs-only, workflow/policy, source/test PR 유형별 샘플링이 필요하다.
- Review result가 branch protection이나 auto-merge eligibility에 직접 연결되지 않아야 한다.
- Required gate 승격은 별도 owner decision으로 다룬다.

## Stop conditions

다음 상황에서는 이 coverage plan 범위를 넘어서므로 작업을 멈추고 owner decision으로 남긴다.

- AI Review Gate prompt 변경이 필요해지는 경우
- GitHub Actions workflow 변경이 필요해지는 경우
- Codex Review를 required gate로 바로 연결해야 하는 경우
- GitHub write permission이 필요한 경우
- `@codex fix`, review-thread resolve, workflow rerun automation이 필요한 경우
- OpenAI API automation 추가가 필요한 경우
- Discord-1a, Discord webhook sender, bot, slash command 구현과 연결되는 경우
- live trading, exchange credentials, risk cap increase, model live promotion과 연결되는 경우

## Owner decisions required

다음 항목은 이 문서가 승인하지 않는다. 모두 future `OWNER_DECISION_REQUIRED`로 남긴다.

- AI Review Gate prompt 보강 허용 여부
- `.github/prompts/ai-review-gate.md` 변경 PR의 scope와 allowed files
- Documentation language consistency를 AI Review Gate에서 얼마나 엄격히 enforce할지
- Codex Review report-only 또는 shadow-review 실험 여부
- Codex Review false positive / false negative 기록 위치
- Merge 후 `@codex review` 사용 정책
- Codex Review automation 또는 required gate 승격 여부

## 다음 단계

권장 순서는 다음과 같다.

1. 이 기준 문서를 merge한다.
2. Post-merge ce-compound로 새 durable lesson 여부를 판단한다.
3. Owner approval 후 AI Review Gate prompt 최소 보강 PR을 별도로 계획한다.
4. Prompt 보강 후 실제 docs-only PR에서 coverage가 개선되는지 확인한다.
5. 그 다음 Codex Review report-only 또는 shadow-review 실험을 별도 owner decision으로 검토한다.

Owner approval 전에는 prompt, workflow, permission, automation을 변경하지 않는다.
