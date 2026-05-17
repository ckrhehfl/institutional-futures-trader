# Risk Engine Interface

이 문서는 `Risk Engine`의 exchange-independent interface contract만 정의합니다. 실제 risk
policy, sizing, leverage, exposure, kill switch, OMS integration, trading engine runtime은 이
단계에서 구현하지 않습니다.

## Scope

- `RiskEvaluationRequest`는 `OrderIntent`를 risk evaluation boundary로 전달하는 immutable
  request envelope입니다.
- `RiskEngine`은 `evaluate(request) -> RiskDecision` 계약만 제공하는 interface입니다.
- `RiskDecision`과 `RiskDecisionStatus`는 core domain model의 기존 타입을 재사용합니다.
- request `metadata`는 기존 safe metadata validation을 사용합니다.
- request `metadata`에는 secret, account identifier, API key, raw exchange payload, raw
  exchange response가 들어갈 수 없습니다.

## Non-Goals

- 실제 risk policy 구현
- sizing, leverage, exposure, liquidation, kill switch logic 구현
- OMS 또는 trading engine 구현
- adapter, REST, WebSocket 구현
- strategy, ML, live trading 구현
- database/storage runtime 구현
- exchange-specific risk rule 또는 exchange payload shape 구현

## Safety Boundary

- Risk interface는 exchange-independent core contract입니다.
- Risk interface는 order submission, execution, adapter calls, persistence, runtime dispatch를
  수행하지 않습니다.
- Risk interface는 `OrderIntent`를 받아 `RiskDecision`을 반환하는 경계만 정의합니다.
- 승인, 거절, 수동 검토의 실제 판단 기준은 후속 policy implementation PR에서 테스트 우선으로
  정의합니다.

## Review Guidance

Risk Engine interface 리뷰는 다음을 확인합니다.

- 기존 `RiskDecision` / `RiskDecisionStatus`를 재사용하는지
- request metadata가 secret/account/API key/raw exchange payload를 거부하는지
- exchange-specific field나 adapter/runtime concern이 core risk interface로 새지 않는지
- 실제 risk policy, OMS, trading engine, live path 구현이 섞이지 않았는지
- regression test가 interface boundary를 충분히 고정하는지
