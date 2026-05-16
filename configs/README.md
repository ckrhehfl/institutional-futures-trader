# Configs

This directory is reserved for public-safe configuration templates and non-secret defaults.

- Do not store real API keys, secrets, tokens, account IDs, wallet addresses, or exchange account details here.
- Do not commit `.env`; use `.env.example` as the only committed environment template.
- Defaults must be paper-safe. The default execution mode is `paper`.
- Live trading configuration must follow `docs/LIVE_TRADING_GATE.md` and must not be enabled by a single config toggle.
