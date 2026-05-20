---
title: AI Review Gate model routing은 deterministic하고 fail closed여야 한다
date: 2026-05-20
category: docs/solutions/security-issues
module: AI Review Gate
problem_type: security_issue
component: development_workflow
symptoms:
  - "AI Review Gate 비용 제어는 required-check 안전성을 낮추지 않으면서 model과 effort를 명시적으로 선택해야 한다."
  - "GitHub changed-file metadata는 pagination되거나 놓치기 쉬운 rename path를 포함할 수 있다."
  - "PR에서 온 label과 filename은 routing logic에서 sanitize하지 않으면 GitHub Actions output으로 들어갈 수 있다."
  - "High-risk review는 더 강한 model을 사용할 수 없을 때 더 싼 model로 조용히 fallback하면 안 된다."
root_cause: missing_workflow_step
resolution_type: workflow_improvement
severity: high
tags: [ai-review-gate, model-routing, github-actions, cost-control, required-check]
---

# AI Review Gate model routing은 deterministic하고 fail closed여야 한다

## Problem

PR #20은 OpenAI API 비용을 더 예측 가능하게 만들기 위해 AI Review Gate에 model routing을 추가했습니다. 오래 남는 위험은 비용 제어가 안전성 축소로 변하는 경우입니다. Gate가 AI에게 자기 model을 고르게 하거나, high-risk PR을 잘못 분류하거나, 더 강한 model을 사용할 수 없을 때 약한 model로 조용히 fallback하면 required check의 의미가 흐려집니다.

## Symptoms

- AI Review Gate가 이전에는 Codex Action 기본 model과 effort 설정에 의존해 비용 예측이 어려웠습니다.
- Routine PR과 docs-only PR은 더 저렴하게 routing하되, workflow, policy, secret, exchange, risk, live-boundary 변경은 더 강한 review를 유지해야 했습니다.
- Review 과정에서 GitHub PR files API pagination 결과는 명시적으로 slurp하고 flatten하지 않으면 단일 JSON document로 취급할 수 없다는 점이 드러났습니다.
- High-risk path detection은 `filename`과 `previous_filename`을 모두 검사해야 하며, nested `.env*` 파일과 nested `AGENTS.md` 파일도 포함해야 했습니다.
- Filename, label, reason 같은 routing metadata는 PR에서 온 값일 수 있으므로 `GITHUB_OUTPUT`에 쓰기 전에 sanitize해야 했습니다.

## What Didn't Work

- Model이 사용할 model이나 effort를 직접 결정하게 두면 비용과 안전성이 non-deterministic해집니다.
- High-risk model을 사용할 수 없을 때 cheap fallback을 쓰면 policy failure가 green check 뒤에 숨습니다.
- Docs-only를 항상 low-risk로 취급하는 것은 너무 넓습니다. Trusted gate 문서와 policy 문서는 그 자체가 high-risk review input입니다.
- `gh api --paginate` 출력을 바로 `json.loads`로 parsing하는 방식은 취약합니다. 여러 page가 하나의 JSON document를 이루지 않을 수 있습니다.
- 현재 file path만 검사하면 `previous_filename`을 통한 rename attack이나 policy 이동을 놓칠 수 있습니다.

## Solution

Codex invocation 전에 model routing을 deterministic workflow step으로 수행합니다.

- `risk_tier`, `codex_model`, `codex_effort`, `risk_reason`은 GitHub API metadata만으로 계산합니다.
- Routing input은 PR labels, changed-file metadata, `filename`, `previous_filename`, base/head repository metadata, diff availability로 제한합니다.
- Routing은 model reasoning이 아니라 shell/Python JSON logic에 둡니다.
- 모든 변경 파일이 `docs/**` 또는 `*.md`이고 trusted policy/gate path가 없으면 low-risk docs-only 변경을 `gpt-5.4-mini` low effort로 routing합니다.
- High-risk path가 없는 일반 source/test/domain 변경은 `gpt-5.4-mini` medium effort로 routing합니다.
- Workflow, prompt, policy, secret, credential, adapter, exchange, OMS, Risk, live-boundary 변경은 `gpt-5.3-codex` high effort로 routing합니다.
- Required AI Gate의 단독 판단자로 nano model을 쓰지 않습니다.
- High-risk model을 사용할 수 없으면 더 싼 model을 조용히 고르지 말고 fail closed 또는 owner policy required로 처리합니다.
- `gh api --paginate --slurp` 또는 동등하게 안전한 collector를 사용하고, file metadata를 검사하기 전에 page array를 flatten합니다.
- PR-derived `filename`, `label`, `risk_reason` 값은 `GITHUB_OUTPUT`에 쓰기 전에 sanitize합니다.

## Why This Works

Deterministic routing은 cost policy와 model judgment를 분리합니다. Workflow가 관찰 가능한 repository metadata로 PR에 필요한 review level을 먼저 결정하고, 선택된 model은 그 고정된 policy 아래에서 diff를 review합니다. 각 run이 tier, model, effort, reason을 job summary와 JSON artifact에 기록하므로 required check를 감사할 수 있습니다.

Failing closed는 security boundary를 보존합니다. 더 강한 model에 접근할 수 없는 high-risk PR이 우연히 low-cost review가 되면 안 됩니다. 그런 경우는 `NEEDS_OWNER_POLICY` 또는 사람이 판단할 수 있는 blocking failure로 드러나야 합니다.

Pagination과 output sanitization은 router 자체가 gate의 일부이기 때문에 중요합니다. File list가 truncate되거나 malformed되면 high-risk path를 놓칠 수 있습니다. PR-derived string을 sanitize하지 않고 `GITHUB_OUTPUT`에 쓰면 악의적인 filename이나 label이 downstream workflow output을 방해할 수 있습니다.

Model routing policy는 live trading과도 독립적입니다. 더 저렴하거나 더 강한 review model을 선택하는 것은 live order submission을 enable하거나, exchange credentials를 바꾸거나, risk cap을 올리거나, model을 live trading으로 promote하지 않습니다.

## Prevention

- Secret-bearing 또는 merge-blocking AI gate에서는 model과 effort를 명시적으로 pin합니다.
- AI Review Gate와 auto-merge workflow를 분리합니다.
- `OPENAI_API_KEY`는 log에 남기지 않고 Codex Action step에만 전달합니다.
- AI Review Gate에서 PR head code를 checkout, build, run, install, import하지 않습니다.
- PR diff와 PR metadata는 untrusted data로 취급합니다.
- Changed files, labels, PR metadata 기반 deterministic routing을 사용하고, model에게 자기 model을 고르게 하지 않습니다.
- GitHub PR files API는 pagination과 함께 `--slurp` 또는 안전한 aggregation 방식을 사용하고, parsing 전에 flatten합니다.
- Path-based policy는 `filename`과 `previous_filename`을 모두 검사합니다.
- Trusted gate/policy docs는 PR이 docs-only여도 high-risk로 취급합니다.
- 모든 PR-derived 값은 `GITHUB_OUTPUT`에 쓰기 전에 sanitize합니다.
- Required AI Gate 판단을 nano model 단독으로 routing하지 않습니다.
- High-risk model에서 더 싼 model로 조용히 fallback하지 않습니다.

## Related Issues

- `docs/AI_REVIEW_GATE.md`
- `.github/workflows/ai-review-gate.yml`
- `.github/prompts/ai-review-gate.md`
- `docs/solutions/security-issues/ai-review-gate-secret-boundary-2026-05-18.md`
- `docs/solutions/security-issues/conditional-auto-merge-trust-boundary-2026-05-19.md`
