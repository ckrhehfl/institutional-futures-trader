# AI Review Gate

이 문서는 Infra PR-3의 AI Review Gate required-check-ready 범위를 정의합니다. 이 gate는 PR diff를
`AGENTS.md`, `docs/PR_REVIEW_PLAYBOOK.md`, `docs/DEVELOPMENT_ROADMAP.md` 기준으로
검토하고 JSON report를 생성합니다.

## Scope

- `pull_request_target` to `main`에서만 실행합니다.
- `openai/codex-action`을 사용합니다.
- `OPENAI_API_KEY`는 GitHub Actions repository secret에서 읽습니다.
- GitHub Actions job summary와 JSON artifact만 생성합니다.
- PR comment는 작성하지 않습니다.
- verdict가 `PASS`일 때만 workflow가 성공합니다.
- verdict가 `FAIL` 또는 `NEEDS_OWNER_POLICY`이면 workflow가 실패합니다.
- missing/invalid JSON은 `NEEDS_OWNER_POLICY` fallback report로 정규화하고 workflow를 실패 처리합니다.
- `PASS` report라도 `owner_decision_required`가 `false`가 아니거나 checks 값이 모두 `pass`가 아니면 workflow가 실패합니다.

## Verdicts

- `PASS`: material scope, safety, validation issue가 없습니다.
- `FAIL`: 현재 PR scope 안의 실제 bug, safety issue, 또는 scope violation 가능성이 있습니다.
- `NEEDS_OWNER_POLICY`: owner 판단이 필요한 policy/scope 충돌이 있습니다.

## Report-Only vs Required-Check-Ready

- Report-only 단계에서는 verdict가 `FAIL`이어도 workflow가 성공했고, 결과는 사람이 읽는 signal이었습니다.
- Required-check-ready 단계에서는 normalized verdict를 마지막 단계에서 읽고 `PASS`만 성공 처리합니다.
- 이 PR은 workflow 동작을 required-check-ready로 바꾸지만 branch protection 설정을 코드로 변경하지 않습니다.
- merge blocking은 머지 후 repository owner가 GitHub branch protection에서 이 workflow를 required check로 지정할 때 활성화됩니다.
- required check 승격은 auto-merge가 아닙니다. PR merge 자동화와 live trading enablement는 별도 정책으로 분리합니다.

## Security Boundary

- `pull_request_target`을 사용하지만 trusted base-branch workflow만 실행합니다.
- permissions는 `contents: read`, `pull-requests: read`로 제한합니다.
- `pull-requests: write` 권한을 사용하지 않습니다.
- secret 값을 출력하지 않습니다.
- fork PR에서는 Codex를 호출하지 않고 `NEEDS_OWNER_POLICY` skip report를 남깁니다.
- `OPENAI_API_KEY`는 Codex action step에만 전달합니다.
- `actions/checkout`은 base branch만 checkout합니다.
- PR head branch 또는 `refs/pull/.../merge`는 checkout하지 않습니다.
- prompt와 guidance는 base branch에서 가져온 trusted copy를 사용합니다.
- PR diff는 `gh pr diff`로 수집한 untrusted text data입니다. Codex는 이 diff를 데이터로만 읽습니다.
- PR code를 checkout, build, test, install, import, 또는 실행하지 않습니다.

## Non-Goals

- auto-merge 구현
- branch protection 자동 변경
- CI workflow 수정
- PR comment 작성
- `pull-requests: write` 권한 추가
- runtime, trading, OMS, Risk policy, Event Bus, Storage, BingX, REST/WebSocket,
  Strategy, ML, Live 구현
- secrets, API key 값, account id, wallet address, `.env` 추가

## Owner Action After Merge

Infra PR-3 merge 후 repository owner가 GitHub branch protection에서 AI Review Gate workflow를
required check로 지정하면 `FAIL`과 `NEEDS_OWNER_POLICY` verdict가 PR merge를 막습니다.

사람의 역할은 일반 코드 품질 reviewer가 아니라 policy, risk, prohibition owner입니다. 사람이 판단해야
하는 영역은 scope 충돌, prohibited implementation, live trading boundary, credential policy,
false positive/false negative adjudication입니다.

## Separation From Trading Policy Gates

이 gate는 main branch merge safety를 다루며 live trading enablement와 연결하지 않습니다. live trading,
exchange credentials, risk cap increase, model live promotion은 계속 별도 policy gate로 봉인합니다.

## Conditional Auto-Merge Policy Boundary

Infra PR-4에서는 별도 auto-merge workflow가 제한적으로 `contents: write` 및
`pull-requests: write` 권한을 가질 수 있습니다. 이 권한은 GitHub auto-merge enable/disable
용도로만 허용됩니다.

이 trusted policy는 PR #15 같은 high-privilege repository automation을 무조건 승인한다는 뜻이
아닙니다. AI Review Gate가 아래 조건을 기준으로 해당 PR을 판단할 수 있게 하는 trusted base 기준입니다.

- `--admin` 사용은 금지합니다.
- branch protection 우회는 금지합니다.
- AI Review Gate workflow와 auto-merge workflow는 분리합니다.
- auto-merge workflow는 `OPENAI_API_KEY` 또는 trading 관련 secrets를 받지 않습니다.
- PR head code checkout, build, run, install, import는 금지합니다.
- fork 또는 external PR은 자동 merge 대상에서 제외합니다.
- high-risk file 변경 PR은 자동 merge 대상에서 제외합니다.
- live trading enablement와 auto-merge는 분리합니다.
- auto-merge workflow는 branch protection과 required checks가 최종 merge gate라는 전제를 약화하지
  않습니다.
