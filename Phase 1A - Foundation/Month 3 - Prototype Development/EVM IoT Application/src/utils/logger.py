"""
Logger for VoteGuard Pro EVM
Language: Python
Handles: Local and remote audit logging
"""

class Logger:
    @staticmethod
    def log(event):
        print(f"[LOG] {event}")
        # Write to encrypted local storage
        from cryptography.fernet import Fernet
        key = b'your-encryption-key'  # Replace with a securely stored key
        cipher_suite = Fernet(key)
        encrypted_event = cipher_suite.encrypt(event.encode('utf-8'))
        with open("audit_log.enc", "ab") as log_file:
            log_file.write(encrypted_event + b"\n")
