## Scope

-

## Non-goals

-

## Allowed files / layers

-

## Validation

-

## Risk boundary

- No secrets, API keys, account ids, wallet addresses, raw exchange credentials, or `.env` content.
- No live trading enablement, exchange credentials, risk cap increase, or model live promotion.
- Core/domain changes remain exchange-independent.

## Owner decision points

- Human owner decisions needed:
- Confirmation needed:

## Out-of-scope handling

- Scope expansions or out-of-scope reviews are classified as `OUT_OF_SCOPE_FOLLOW_UP` or `OWNER_DECISION_REQUIRED`.
- If a change outside Allowed files / layers is needed, do not implement it without an owner decision.

## Prohibited implementation confirmation

This PR does not touch:

- [ ] workflows
- [ ] AI Review Gate
- [ ] auto-merge
- [ ] model routing
- [ ] branch protection
- [ ] live trading
- [ ] credentials/secrets
- [ ] risk cap increase
- [ ] model live promotion
- [ ] OMS/Risk runtime/BingX/strategy/ML/trading engine

## Human role

- Humans are task, policy, risk, and prohibition owners.
- Code quality is validated by CI, deterministic checks, AI Review Gate, and policy gates.

## Review guidance

- Classify review comments with `docs/PR_REVIEW_PLAYBOOK.md` before editing.
- P1/P2 comments outside this PR's scope should become follow-up or owner-decision items.
- Do not expand scope to satisfy optional/style or out-of-scope review comments.

## Follow-up items

-

## Compound learning note

- What repeated mistake or durable lesson came from this PR?
- Where was the prevention added: test, `AGENTS.md`, PR template, docs, playbook, CI/checklist, or follow-up?
- Is `/ce-compound` planned after merge, or was a manual compound note added in this PR?

## This PR intentionally does not implement...

-
