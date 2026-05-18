# AI Review Gate

이 문서는 Infra PR-2의 AI Review Gate report-only 범위를 정의합니다. 이 gate는 PR diff를
`AGENTS.md`, `docs/PR_REVIEW_PLAYBOOK.md`, `docs/DEVELOPMENT_ROADMAP.md` 기준으로
검토하고 JSON report를 생성합니다.

## Scope

- `pull_request` to `main`에서만 실행합니다.
- `openai/codex-action`을 사용합니다.
- `OPENAI_API_KEY`는 GitHub Actions repository secret에서 읽습니다.
- GitHub Actions job summary와 JSON artifact만 생성합니다.
- PR comment는 작성하지 않습니다.
- verdict가 `FAIL`이어도 workflow는 성공 처리합니다.

## Verdicts

- `PASS`: material scope, safety, validation issue가 없습니다.
- `FAIL`: 현재 PR scope 안의 실제 bug, safety issue, 또는 scope violation 가능성이 있습니다.
- `NEEDS_OWNER_POLICY`: owner 판단이 필요한 policy/scope 충돌이 있습니다.

## Security Boundary

- `pull_request_target`은 사용하지 않습니다.
- permissions는 `contents: read`, `pull-requests: read`로 제한합니다.
- `pull-requests: write` 권한을 사용하지 않습니다.
- secret 값을 출력하지 않습니다.
- fork PR 또는 `OPENAI_API_KEY`가 없는 실행에서는 Codex를 호출하지 않고 skip report를 남깁니다.
- prompt와 guidance는 base branch에서 가져온 trusted copy를 사용합니다. PR checkout의 prompt 변경은
  Codex 실행에 사용하지 않습니다.
- PR code를 실행하지 않고 diff와 repository guidance만 검토합니다.

## Non-Goals

- auto-merge 구현
- required check 승격
- CI workflow 수정
- branch protection 변경
- runtime, trading, OMS, Risk policy, Event Bus, Storage, BingX, REST/WebSocket,
  Strategy, ML, Live 구현
- secrets, API key 값, account id, wallet address, `.env` 추가

## Promotion Criteria

Infra PR-3에서 merge-blocking required check로 승격하려면 report-only 결과를 여러 PR에서
관찰하고 false positive, false negative, owner policy conflict 사례를 정리해야 합니다. 승격 전에는
verdict schema, owner decision flow, branch protection 변경, 그리고 live/trading/policy gate와의
분리를 별도로 승인해야 합니다.
