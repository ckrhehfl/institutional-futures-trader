# Live Trading Gate

## Gate Intent

Live trading can lose real money. It must never be enabled casually, accidentally, or by a single config toggle.

Default mode is always `paper`. `live` is disabled unless every gate condition below is satisfied.

## Hard Requirements

Live activation requires all of the following. Paper evidence and demo evidence are both mandatory before live trading:

- explicit human approval for live trading;
- separate live-only environment variables;
- runtime confirmation that live mode was intentionally requested;
- non-withdrawal exchange API keys;
- documented evidence from paper trading;
- documented evidence from demo trading;
- passing tests for `Risk Engine`, `OMS`, `Order Lifecycle`, `Position/PnL`, and `Reconciliation`;
- tested kill switch and max loss behavior;
- successful reconciliation of orders, positions, balances, leverage, and margin mode;
- restart recovery verification;
- failure handling verification for API outage, WebSocket disconnect, stale data, partial fills, and mismatches.

Demo evidence is not optional. If BingX demo/sandbox is formally unavailable, live activation still requires a separately approved substitute verification plan. That plan must document why demo evidence cannot be produced, what additional paper/replay/reconciliation evidence replaces it, and who approved the substitution.

## Prohibited Activation Pattern

Live must not be enabled by only changing:

```text
MODE=live
```

or any equivalent single config value.

Live must require multiple independent confirmations across policy, environment, runtime, and operator approval.

`ExecutionGateway` must not select `LiveExecutionVenue` unless these confirmations are all present. Any ambiguous state must resolve to `PaperExecutionVenue` or fail closed.

## Public Repository Safety

- Real API key, secret, token, account id, or exchange account details must never be committed.
- `.env` must never be committed.
- `.env.example` is allowed and must not contain real credentials.
- API keys must have withdrawal permission disabled.
- Logs and audit records must not reveal secret values.
- Secret scanning and log redaction must be in place before live credential loading exists.

## Required Runtime Guards

Runtime must verify:

- requested mode is `live`;
- live environment variables are present and explicitly named for live use;
- paper/demo-only credentials are not being reused ambiguously;
- operator approval artifact or confirmation is present;
- `ExecutionGateway` selected `LiveExecutionVenue` only after live guard approval;
- kill switch is inactive but available;
- max loss limits are configured;
- reconciliation is current;
- market and account data are fresh.

If any check fails, live trading must not start.

## Evidence Requirements

Before live trading, maintain evidence for:

- profitable or acceptable strategy/risk performance in paper/demo context;
- bounded drawdown and loss behavior;
- correct fee, funding, slippage, realized PnL, and unrealized PnL accounting;
- reconciliation correctness;
- restart recovery;
- latency within target under expected internal load;
- failure handling behavior.

## Ongoing Live Conditions

Live trading must stop or reduce risk when:

- kill switch is activated;
- max loss limit is reached;
- exchange API is unavailable;
- WebSocket data is stale;
- internal and exchange state diverge;
- liquidation risk exceeds policy;
- credentials or account state are ambiguous;
- restart recovery is incomplete.

If the system cannot prove it is safe to continue, it must stop increasing risk.
