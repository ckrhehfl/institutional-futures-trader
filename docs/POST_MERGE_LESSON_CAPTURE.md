# Post-Merge Lesson Capture

이 문서는 Infra PR-6의 post-merge lesson capture v0 범위를 정의합니다. 이 workflow는 merge된 PR에서 durable lesson 후보를 놓치지 않기 위한 read-only report를 생성합니다.

## Purpose

- PR merge 이후 배울 만한 교훈 후보를 deterministic metadata 기반으로 요약합니다.
- 결과는 GitHub Actions job summary와 artifact로만 남깁니다.
- Durable lesson이 없으면 `no lesson captured`가 정상 결과입니다.
- 사람이 artifact를 검토한 뒤 필요할 때만 `/ce-compound` 또는 docs-only PR로 이어갑니다.

## Triggers

- `pull_request_target` with `types: [closed]`
  - PR이 실제로 merged된 경우에만 실행합니다.
- `workflow_dispatch`
  - 이미 merge된 PR number를 입력해 수동으로 다시 점검할 수 있습니다.

## Inputs

Workflow는 GitHub API metadata만 읽습니다.

- PR number
- PR number
- label count
- changed file category counts
- merge commit SHA
- review count와 review comment count
- check conclusion summary, 가능한 경우

PR diff, body, comments, labels, file names는 untrusted text data로만 취급합니다. v0 report는 free-form PR title/body, raw labels, raw file paths를 artifact에 내보내지 않습니다.

## Outputs

- GitHub Actions job summary
- JSON artifact
- Markdown artifact

Workflow는 PR comment, GitHub Issue, branch, commit, pull request를 만들지 않습니다.

## Lesson Candidate Heuristic

이 workflow는 AI 판정을 하지 않습니다. OpenAI API를 사용하지 않고 deterministic signal만 계산합니다.

Candidate signal 예시는 다음과 같습니다.

- security, secret, permission, trust boundary 관련 label 또는 path
- CI, AI Gate, auto-merge, policy gate 관련 변경
- owner decision, scope, review guardrail 관련 신호
- review comment가 반복 가능한 policy 또는 security 키워드를 포함하는 경우
- `docs/solutions/**`에 반영할 만한 learning note 관련 신호

단순 구현 요약은 durable lesson이 아닙니다. 애매하면 자동으로 learning note를 만들지 않고, 사람이 artifact를 검토합니다.

## Security Boundary

- PR head code를 checkout, build, run, install, import하지 않습니다.
- Fork 또는 external PR content를 실행하지 않습니다.
- Untrusted text를 shell command로 실행하거나 `eval`하지 않습니다.
- Secret 값은 출력하지 않습니다.
- Secret-like value는 report에 그대로 남지 않도록 redaction합니다.
- Workflow는 redaction self-check와 generated output scan을 수행합니다.
- Artifact와 job summary에는 raw PR title/body/labels/file paths를 출력하지 않습니다.
- `--admin`을 사용하지 않습니다.
- Branch protection을 우회하지 않습니다.
- Auto-merge, AI Review Gate verdict, live trading enablement와 연결하지 않습니다.
- Exchange credentials, risk cap increase, model live promotion과 연결하지 않습니다.

## Permissions

Workflow는 read-only 권한만 사용합니다.

- `contents: read`
- `pull-requests: read`
- `checks: read`

금지 권한:

- `contents: write`
- `pull-requests: write`
- `issues: write`
- `actions: write`

## Non-Goals

- Learning note 자동 커밋
- Docs-only PR 자동 생성
- Follow-up Issue 자동 생성
- PR comment 작성
- AI Review Gate workflow, prompt, model routing 수정
- Auto-merge workflow 또는 policy 수정
- CI workflow 수정
- Branch protection 설정 변경
- Live trading gate 변경
- OMS, Risk runtime, BingX REST/WebSocket, strategy, ML, trading engine, live trading, storage runtime, event bus runtime 구현
- Live trading enablement, exchange credentials, risk cap increase, model live promotion과 연결

## Human Review Flow

1. Workflow가 merged PR의 lesson candidate report를 생성합니다.
2. 사람이 job summary 또는 artifact를 확인합니다.
3. `lesson_candidate`가 `true`이고 재사용 가능한 교훈이 있으면 `/ce-compound`를 실행하거나 docs-only PR을 만듭니다.
4. `lesson_candidate`가 `false`이면 `no lesson captured`로 종료합니다.
