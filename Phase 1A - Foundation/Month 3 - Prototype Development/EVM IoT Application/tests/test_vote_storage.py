import json
import os

# Ensure src is importable
import sys
import tempfile
import unittest
from datetime import datetime

SRC_PATH = os.path.join(os.path.dirname(__file__), "..", "src")
sys.path.insert(0, os.path.abspath(SRC_PATH))

from backend.vote_storage import VoteStorage
from cryptography.fernet import Fernet


class TestVoteStorage(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.storage_file = os.path.join(self.tmpdir.name, "votes.json")
        self.key_file = os.path.join(self.tmpdir.name, "key.key")
        # Generate a test key
        key = Fernet.generate_key()
        with open(self.key_file, "wb") as f:
            f.write(key)
        # Initialize storage
        self.vs = VoteStorage(storage_file=self.storage_file, key_file=self.key_file)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_store_and_read_vote(self):
        ts = datetime.now().isoformat()
        self.vs.store_vote("State Assembly", "Party A", timestamp=ts)
        # Read back encrypted file and decrypt
        with open(self.storage_file, "rb") as f:
            encrypted = f.read()
        with open(self.key_file, "rb") as f:
            key = f.read()
        cipher = Fernet(key)
        votes = json.loads(cipher.decrypt(encrypted).decode("utf-8"))
        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0]["election_type"], "State Assembly")
        self.assertEqual(votes[0]["party_name"], "Party A")
        self.assertEqual(votes[0]["timestamp"], ts)


if __name__ == "__main__":
    unittest.main()
