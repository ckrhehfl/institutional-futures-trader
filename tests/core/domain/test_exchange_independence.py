from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOMAIN_ROOT = ROOT / "src" / "trading_system" / "core" / "domain"
VALIDATION_FILE = DOMAIN_ROOT / "validation.py"


def test_core_domain_does_not_contain_exchange_specific_field_or_client_terms() -> None:
    forbidden_terms = [
        "orderId",
        "clientOrderId",
        "symbolName",
        "errCode",
        "errMsg",
        "requests",
        "websocket",
        "httpx",
        "aiohttp",
        "connect(",
        "submit_order",
    ]

    scanned = {path: path.read_text(encoding="utf-8") for path in DOMAIN_ROOT.rglob("*.py")}

    violations = [
        f"{path.relative_to(ROOT).as_posix()}:{term}"
        for path, content in scanned.items()
        for term in forbidden_terms
        if term in content
    ]

    assert violations == []


def test_exchange_specific_metadata_terms_only_exist_in_validator_allowlist() -> None:
    allowed_terms = ["bingx", "api_key", "secret", "token", "payload", "response"]

    scanned = {
        path: path.read_text(encoding="utf-8")
        for path in DOMAIN_ROOT.rglob("*.py")
        if path != VALIDATION_FILE
    }

    violations = [
        f"{path.relative_to(ROOT).as_posix()}:{term}"
        for path, content in scanned.items()
        for term in allowed_terms
        if term in content
    ]

    assert violations == []
