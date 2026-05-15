from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


SECRET_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"gh[pousr]_[A-Za-z0-9_]{20,}",
        r"sk-[A-Za-z0-9]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"(?im)^(api[_-]?key|secret|token|account[_-]?id)\s*=\s*['\"]?[A-Za-z0-9_\-]{12,}",
    ]
]


def test_env_file_is_not_present_and_template_is_allowed() -> None:
    assert not (ROOT / ".env").exists()
    assert (ROOT / ".env.example").is_file()

    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    ignored_entries = {
        line.strip()
        for line in gitignore.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert ".env" in ignored_entries
    assert "!.env.example" in ignored_entries


def test_env_example_contains_no_real_looking_secrets() -> None:
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")

    matches = [
        pattern.pattern
        for pattern in SECRET_PATTERNS
        if pattern.search(env_example)
    ]

    assert matches == []
    assert "TRADING_MODE=paper" in env_example
    assert "LIVE_TRADING_ENABLED=false" in env_example


def test_secret_prevention_policy_is_configured() -> None:
    pre_commit = (ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "detect-secrets" in pre_commit

    config_readme = (ROOT / "configs" / "README.md").read_text(encoding="utf-8")
    assert ".env" in config_readme
    assert "secret" in config_readme.lower()
    assert "paper" in config_readme.lower()
