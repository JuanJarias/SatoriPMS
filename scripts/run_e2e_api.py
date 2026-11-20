#!/usr/bin/env python3
"""Arranca Uvicorn aislado contra *_test para pruebas E2E de Playwright sin tocar satoripms."""

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tests.backend.conftest import (  # noqa: E402
    _build_test_database_url,
    _ensure_test_database_and_schema,
)
import uvicorn  # noqa: E402


def main() -> None:
    test_db_url = _build_test_database_url()
    os.environ["DATABASE_URL"] = test_db_url
    os.environ.setdefault("ENVIRONMENT", "test")
    _ensure_test_database_and_schema(test_db_url)

    port = int(os.environ.get("E2E_API_PORT", "8081"))
    uvicorn.run(
        "apps.api.main:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
