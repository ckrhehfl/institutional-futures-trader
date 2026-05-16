from __future__ import annotations

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))


def test_pyproject_targets_python_312_and_src_layout() -> None:
    pyproject = load_pyproject()

    assert pyproject["project"]["requires-python"] == ">=3.12"
    assert pyproject["tool"]["setuptools"]["package-dir"] == {"": "src"}
    assert pyproject["tool"]["setuptools"]["packages"]["find"]["where"] == ["src"]


def test_pytest_and_dev_tooling_are_configured() -> None:
    pyproject = load_pyproject()

    assert pyproject["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests"]
    assert pyproject["tool"]["pytest"]["ini_options"]["pythonpath"] == ["src"]

    dev_dependencies = set(pyproject["project"]["optional-dependencies"]["dev"])
    assert {"pytest>=8", "ruff>=0.8", "pre-commit>=4", "detect-secrets>=1.5"}.issubset(
        dev_dependencies
    )


def test_ruff_is_configured_for_project_sources() -> None:
    pyproject = load_pyproject()

    assert pyproject["tool"]["ruff"]["target-version"] == "py312"
    assert pyproject["tool"]["ruff"]["src"] == ["src", "tests"]
