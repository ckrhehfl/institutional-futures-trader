# Domain Events v0

이 문서는 exchange-independent core domain event contract의 v0 범위를 정의합니다. Domain
Events v0는 감사와 replay를 고려한 안정적인 event shape를 제공하지만, event bus runtime,
database/storage runtime, adapter translation, execution path는 구현하지 않습니다.

## Scope

- `DomainEvent`는 core domain에서 발생한 사실을 기록하는 immutable event envelope입니다.
- `event_type`은 lowercase dotted name을 사용합니다. 예: `signal.generated`,
  `order.intent.created`, `risk.decision.recorded`.
- `occurred_at`은 timezone-aware `datetime`이어야 합니다.
- `subject`는 event가 설명하는 domain object id입니다.
- `correlation_id`와 `causation_id`는 선택 값이며, replay와 audit 추적을 위한 안정적인 id만
  담습니다.
- `data`와 `metadata`는 primitive value만 허용합니다.
- `data`와 `metadata`에는 secret, account identifier, API key, raw exchange payload, raw
  exchange response가 들어갈 수 없습니다.

## Non-Goals

- event bus, queue, publisher, subscriber 구현
- database/storage runtime 구현
- REST/WebSocket 또는 exchange adapter translation 구현
- trading engine, OMS, Risk Engine 구현
- paper/demo/live execution path 구현
- strategy/ML/live trading 구현

## Safety Boundary

- Domain event는 exchange-independent fact만 기록합니다.
- Exchange adapter는 raw exchange payload를 core event에 직접 넣지 않습니다.
- Account id, API key, secret, token, wallet address처럼 credential 또는 account identifier로
  볼 수 있는 값은 event `data`와 `metadata` 모두에서 금지합니다.
- `metadata`는 tracing, policy label, operator-safe note처럼 공개 저장 가능한 값만 담습니다.

## Review Guidance

Domain Events v0 리뷰는 다음을 확인합니다.

- event type naming이 stable하고 exchange-independent인지
- `occurred_at`이 timezone-aware인지
- `data`와 `metadata`가 immutable하고 primitive-only인지
- secret/account/API key/raw exchange payload가 event에 들어갈 수 없는지
- event bus, storage, adapter, execution path가 이 PR에 섞이지 않았는지
