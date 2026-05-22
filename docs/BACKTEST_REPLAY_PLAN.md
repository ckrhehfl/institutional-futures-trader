# BACKTEST / HISTORICAL REPLAY PLAN

## Purpose

이 문서는 Step 7 `Backtest / Historical Replay`의 v0 경계를 docs-first로 고정하기 위한 계획 문서입니다.
현재 단계의 목적은 full backtest engine 구현이 아니라, exchange-independent deterministic replay contract를 먼저 정의하는 것입니다.

## Owner-approved scope

- Step 6 OMS State Machine v0 완료 이후, Step 7을 current implementation step으로 진행합니다.
- Step 7은 docs-only PR 범위에서 deterministic replay contract planning을 수행합니다.
- future package naming preference는 `core/backtest`를 사용합니다.
- 본 단계는 core domain boundary 정렬과 contract 후보 정의에 한정됩니다.

## Non-goals

- backtest runtime engine 구현
- event bus runtime, storage runtime, database runtime 구현
- market data loader 구현
- external data fetch 구현
- strategy/ML alpha 구현
- exchange adapter 구현
- execution venue runtime 구현
- `PaperExecutionVenue`, `DemoExecutionVenue`, `LiveExecutionVenue` 구현 또는 연결
- live/demo trading integration
- real order submission path 구현
- BingX, REST, WebSocket 연동 구현

## Determinism policy

- 동일한 replay input과 동일한 replay assumptions를 사용하면 동일한 output artifact를 생성해야 합니다.
- deterministic replay 결과는 timestamp ordering, idempotent event handling, stable validation rule에 의해 재현 가능해야 합니다.
- non-deterministic 요소(실시간 clock, 외부 API 응답, 랜덤 seed 미고정)는 Step 7 v0 경계에서 허용하지 않습니다.
- deterministic 보장은 contract 수준에서 먼저 명시하고, 구현은 후속 PR에서 test-first로 진행합니다.

## Input candidates

Step 7 v0에서 제안하는 contract-only 입력 후보는 다음과 같습니다.

- `BacktestReplayRequest`
  - replay 목적, scope, 실행 정책을 담는 상위 요청 envelope
- `BacktestReplayInput`
  - replay 대상 event stream reference, scenario metadata, 검증 정책 참조
- `ReplayTimeWindow`
  - 시작/종료 시점, timezone normalization, ordering 기준
- `ReplayAssumptions`
  - 수수료/슬리피지/펀딩/PnL/드로우다운 처리에 대한 가정 정의
  - 단, Step 7에서는 계산 구현이 아니라 assumption contract만 정의

## Output candidates

Step 7 v0에서 제안하는 contract-only 출력 후보는 다음과 같습니다.

- `BacktestReplayResult`
  - replay 실행 요약, deterministic 검증 결과, 산출물 참조 정보
- `ReplayValidationSummary`
  - 입력 검증/경계 검증/정합성 검증 상태
- Domain-level replay artifact 후보
  - `DomainEvent` replay trace
  - `OrderIntent` -> `Order` -> `Fill` lifecycle 관찰 결과
  - `Fee`, `FundingFee`, `PnL`, `Position` 관련 검증 가능한 요약 산출물
  - `RiskDecision` history alignment 결과
  - `ReconciliationEvent` 관찰 가능성 및 drift 검증 포인트

## Validation boundary

Step 7 v0는 구현이 아니라 검증 경계 정의에 집중합니다.

- 포함:
  - deterministic replay contract 요구사항 문서화
  - input/output contract 후보 정의
  - 도메인 이벤트 및 OMS state transition 재현 조건 정의
  - replay validation summary 기준 정의
- 제외:
  - runtime execution path
  - 외부 데이터 로딩
  - 거래소 API 연동
  - 실거래/모의거래 venue 실행

## Relationship to OMS State Machine

- Step 6에서 고정된 OMS State Machine v0 transition rule은 Step 7 replay 검증의 핵심 전제입니다.
- replay는 `OrderIntent`, `Order`, `Fill` 흐름이 OMS state transition invariant를 위반하지 않는지 검증해야 합니다.
- Step 7은 OMS runtime을 추가하지 않으며, Step 6의 pure helper 경계를 유지한 채 replay contract에서 참조 관계만 고정합니다.

## Relationship to RiskDecision history

- replay contract는 `RiskDecision` history를 deterministic audit artifact로 남길 수 있어야 합니다.
- replay 과정에서 risk boundary 우회 여부를 판별할 수 있도록 decision lineage를 추적 가능하게 정의합니다.
- `RiskDecision`은 strategy/ML 신호보다 상위의 최종 권한 경계를 유지해야 하며, Step 7에서는 이 정책을 문서로 고정합니다.

## Domain relationship map

Step 7 v0 planning boundary에서 다음 관계를 명시합니다.

- `TradingMode.BACKTEST`는 historical replay contract를 실행하는 mode로 정의합니다.
- `ExecutionVenue.BACKTEST`는 runtime venue 구현이 아니라 contract 상의 logical venue 식별자로만 사용합니다.
- `DomainEvent`는 replay의 기본 입력/검증 단위입니다.
- `OrderIntent`, `Order`, `Fill`은 OMS State Machine invariant 기반으로 재생 및 검증됩니다.
- `Fee`, `FundingFee`, `PnL`, `Position`은 계산 구현이 아니라 replay 결과 산출물의 contract 항목으로만 정의합니다.
- `RiskDecision`은 replay 중 risk authority history를 검증하기 위한 핵심 감사 축입니다.
- `ReconciliationEvent`는 replay 결과와 상태 정합성 확인을 위한 경계 이벤트로 취급합니다.

## Future contract-only implementation proposal

다음 항목은 후속 PR에서 test-first로 다룰 contract-only 구현 후보입니다.

- `BacktestReplayRequest`
- `BacktestReplayInput`
- `BacktestReplayResult`
- `ReplayTimeWindow`
- `ReplayAssumptions`
- `ReplayValidationSummary`

후속 PR에서도 본 문서의 non-goals를 유지하며, runtime engine/adapter/venue 구현은 범위 밖으로 유지합니다.

## Stop conditions

다음 조건 중 하나라도 발생하면 Step 7 구현 PR을 중단하고 owner 재확인이 필요합니다.

- deterministic replay contract보다 runtime 구현이 선행되어야 한다는 요구가 발생한 경우
- exchange-specific 로직이 core domain boundary로 유입되는 경우
- live/demo/paper execution venue runtime 추가가 선행 조건으로 제시되는 경우
- strategy/ML/external fetch 구현이 Step 7 필수 조건으로 요구되는 경우
- docs-only 범위를 벗어난 source/test/runtime 코드 변경이 필요한 경우

## Open owner decisions for future PRs

- `OWNER_DECISION_REQUIRED`: replay input event source의 canonical format과 versioning policy
- `OWNER_DECISION_REQUIRED`: `ReplayAssumptions`의 기본값 프로파일(보수적/중립/공격적) 정책
- `OWNER_DECISION_REQUIRED`: replay 결과 artifact의 보존 기간 및 감사 저장소 정책
- `OWNER_DECISION_REQUIRED`: `ReconciliationEvent` drift 허용 오차의 도메인별 임계치
- `Future owner decision`: fees/slippage/funding/PnL/drawdown 계산 구현의 단계별 도입 순서
