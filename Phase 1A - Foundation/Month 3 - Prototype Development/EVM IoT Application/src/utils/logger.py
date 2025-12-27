"""
Logger for VoteGuard Pro EVM
Language: Python
Handles: Local and remote audit logging (encrypted)
"""

import os
from typing import Optional

try:
    # Load environment variables from a local .env if present
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

from cryptography.fernet import Fernet, InvalidToken


class Logger:
    @staticmethod
    def _load_fernet_key() -> Optional[bytes]:
        """
        Load Fernet key from environment or key file.
        Priority:
          1) FERNET_KEY (base64-encoded) env var
          2) FERNET_KEY_PATH env var (path to key file)
          3) fallback to ./key.key relative to working dir
        """

        env_key = os.getenv("FERNET_KEY")
        if env_key:
            try:
                return env_key.encode("utf-8")
            except Exception:
                print("[SEC] Invalid FERNET_KEY env value.")
                return None

        key_path = os.getenv("FERNET_KEY_PATH", "key.key")
        try:
            with open(key_path, "rb") as f:
                return f.read()
        except FileNotFoundError:
            print(f"[SEC] Key file not found at {key_path}.")
            return None
        except Exception as e:
            print(f"[SEC] Failed to read key file: {e}")
            return None

    @staticmethod
    def log(event: str) -> None:
        print(f"[LOG] {event}")

        key = Logger._load_fernet_key()
        audit_path = os.getenv("AUDIT_LOG_PATH", "audit_log.enc")

        if not key:
            print("[SEC] No encryption key available; audit event NOT persisted.")
            return

        try:
            cipher_suite = Fernet(key)
            encrypted_event = cipher_suite.encrypt(event.encode("utf-8"))
        except (ValueError, InvalidToken) as e:
            print(f"[SEC] Failed to encrypt audit event: {e}")
            return

        try:
            with open(audit_path, "ab") as log_file:
                log_file.write(encrypted_event + b"\n")
        except Exception as e:
            print(f"[SEC] Failed to write audit log: {e}")
