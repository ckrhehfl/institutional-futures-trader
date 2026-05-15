from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def test_python_package_skeleton_exists_and_imports() -> None:
    expected_paths = [
        ROOT / "pyproject.toml",
        ROOT / ".gitignore",
        ROOT / ".env.example",
        ROOT / ".pre-commit-config.yaml",
        ROOT / "configs" / "README.md",
        SRC / "trading_system" / "__init__.py",
        SRC / "trading_system" / "py.typed",
    ]

    missing = [path.relative_to(ROOT).as_posix() for path in expected_paths if not path.exists()]
    assert missing == []

    sys.path.insert(0, str(SRC))
    try:
        package = importlib.import_module("trading_system")
    finally:
        sys.path.remove(str(SRC))

    assert package.__all__ == ["__version__"]
    assert isinstance(package.__version__, str)


def test_skeleton_does_not_include_trading_implementation() -> None:
    forbidden_paths = [
        SRC / "trading_system" / "engine.py",
        SRC / "trading_system" / "risk.py",
        SRC / "trading_system" / "oms.py",
        SRC / "trading_system" / "strategy.py",
        SRC / "trading_system" / "ml.py",
        SRC / "trading_system" / "live.py",
        SRC / "trading_system" / "adapters" / "exchanges" / "bingx",
    ]

    present = [path.relative_to(ROOT).as_posix() for path in forbidden_paths if path.exists()]
    assert present == []
