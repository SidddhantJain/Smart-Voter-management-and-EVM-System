"""
Vote Storage Backend for VoteGuard Pro EVM
Language: Python
Handles: Secure storage of votes
"""
import json
import os
from datetime import datetime
from cryptography.fernet import Fernet

class VoteStorage:
    def __init__(self, storage_file="votes.json", key_file="key.key"):
        self.storage_file = storage_file
        self.key_file = key_file
        self.key = self.load_or_generate_key()
        self.cipher = Fernet(self.key)
        # Ensure the storage file exists
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, "wb") as f:
                f.write(self.cipher.encrypt(json.dumps([]).encode()))

    def load_or_generate_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key

    def store_vote(self, election_type, party_name, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        vote = {
            "election_type": election_type,
            "party_name": party_name,
            "timestamp": timestamp
        }
        with open(self.storage_file, "rb+") as f:
            encrypted_data = f.read()
            votes = json.loads(self.cipher.decrypt(encrypted_data).decode())
            votes.append(vote)
            f.seek(0)
            f.write(self.cipher.encrypt(json.dumps(votes).encode()))
        print(f"[BACKEND] Vote stored securely: {vote}")

    def initialize_storage(self):
        # Reinitialize the storage file with valid encrypted data
        with open(self.storage_file, "wb") as f:
            f.write(self.cipher.encrypt(json.dumps([]).encode()))
        print("[BACKEND] Storage file reinitialized.")

if __name__ == "__main__":
    backend = VoteStorage()
    backend.initialize_storage()
    backend.store_vote("State Assembly", "Party A")
