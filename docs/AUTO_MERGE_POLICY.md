# Auto Merge Policy

This document defines the Infra PR-4 conditional auto-merge policy. Auto-merge is a main branch merge convenience, not live trading enablement.

## Scope

- Enable GitHub auto-merge only for eligible same-repository PRs targeting `main`.
- Let GitHub branch protection and required checks decide whether the PR can actually merge.
- Keep auto-merge separate from CI, AI Review Gate, live trading gates, and post-merge lesson capture.

## Owner-Approved Boundary

Infra PR-4 explicitly approves adding `.github/workflows/auto-merge.yml` with `pull_request_target`, `contents: write`, and `pull-requests: write` for one narrow purpose: enabling or disabling GitHub auto-merge for eligible same-repository PRs. This approval does not extend to branch protection changes, PR comments, AI Review Gate changes, repository secrets, trading secrets, workflow bypasses, direct merges, or live trading enablement.

## Non-Goals

- Auto-merge does not enable live trading.
- Auto-merge does not configure branch protection as code.
- Auto-merge does not modify the AI Review Gate.
- Auto-merge does not post PR comments.
- Auto-merge does not use `OPENAI_API_KEY` or trading-related secrets.
- Auto-merge does not implement GitHub Issue or PR templates; that belongs to Infra PR-5.
- Auto-merge does not implement post-merge lesson capture automation; that belongs to Infra PR-6.

## Eligibility

A PR is eligible only when all of these are true:

- The PR targets `main`.
- The PR comes from the same repository, not a fork or external repository.
- The PR is open.
- The PR is not a draft.
- The PR does not have a blocking label:
  - `do-not-merge`
  - `blocked`
  - `owner-decision-required`
  - `security-review-required`
  - `manual-merge-only`
- The PR does not change high-risk files or paths:
  - `.github/workflows/**`
  - `.github/prompts/**`
  - `AGENTS.md`
  - `docs/AI_REVIEW_GATE.md`
  - `docs/AUTO_MERGE_POLICY.md`
  - `docs/PR_REVIEW_PLAYBOOK.md`
  - `docs/LIVE_TRADING_GATE.md`
  - `docs/DEVELOPMENT_ROADMAP.md`
  - `.pre-commit-config.yaml`
  - `pyproject.toml`
  - `.secrets.baseline`
  - `.env*`
  - `**/*secret*`
  - `**/*credential*`
  - `**/*key*`
  - `src/trading_system/adapters/exchanges/**`
  - files or paths directly related to live trading enablement, model live promotion, or risk cap changes

For renamed files, both the previous path and current path must pass the high-risk exclusion check.

If a same-repository PR is retargeted away from `main`, it becomes ineligible and the workflow may disable any existing GitHub auto-merge for that PR.

## Branch Protection and Required Checks

The auto-merge workflow does not bypass branch protection. It only asks GitHub to enable auto-merge with:

```shell
gh pr merge <PR_NUMBER> --auto --squash --match-head-commit <HEAD_SHA>
```

GitHub branch protection remains the final merge authority. CI and the AI Review Gate required check must pass before GitHub can complete the merge. If a required check fails, auto-merge waits or does not merge.

The repository owner must separately confirm in GitHub settings that:

- Allow auto-merge is enabled.
- Required checks include deterministic CI.
- Required checks include the AI Review Gate after Infra PR-3.
- Branch protection does not allow this workflow to bypass required checks.

## AI Review Gate Separation

The auto-merge workflow does not invoke Codex, does not read `OPENAI_API_KEY`, and does not change the AI Review Gate workflow. AI Review Gate remains an independent required check. If AI Review Gate returns `FAIL` or `NEEDS_OWNER_POLICY`, branch protection blocks the merge.

## Fork and External PRs

Fork PRs and external repository PRs are not auto-merge eligible. They require manual owner handling because they may have different trust and permission boundaries.

## Owner Decision and Blocked States

The `owner-decision-required`, `security-review-required`, `manual-merge-only`, `blocked`, and `do-not-merge` labels opt a PR out of auto-merge. These labels represent policy, risk, or scope conditions that automation should not resolve.

When a same-repository PR becomes ineligible after auto-merge was already enabled, the workflow disables GitHub auto-merge for that PR. This keeps blocking labels and high-risk file changes effective after the initial eligibility decision.

Human owners remain responsible for policy, risk, prohibited implementation, credential handling, and live trading boundary decisions. They are not the default code quality reviewer.

## Live Trading Separation

Main branch auto-merge is not live trading enablement. Live trading, exchange credentials, risk cap increase, and model live promotion remain sealed behind separate policy gates. A PR merging to `main` must not grant live order submission capability by itself.

## Rollback

If auto-merge behaves incorrectly:

- Disable the `Auto Merge` workflow in GitHub Actions, or revert `.github/workflows/auto-merge.yml`.
- Add `manual-merge-only` to affected PRs while investigating.
- Do not weaken CI, AI Review Gate, or live trading policy gates as a rollback shortcut.
