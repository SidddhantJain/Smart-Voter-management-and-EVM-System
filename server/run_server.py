from __future__ import annotations

try:
    from .verification_server import main
except Exception:  # pragma: no cover - allows direct script execution
    from verification_server import main


if __name__ == "__main__":
    raise SystemExit(main())
