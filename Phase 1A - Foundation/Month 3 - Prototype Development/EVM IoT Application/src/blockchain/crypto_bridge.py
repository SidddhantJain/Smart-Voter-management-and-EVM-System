"""
Python FFI bridge to Rust cryptography module (crypto.rs)
Handles: vote hashing, digital signature, and verification
"""
import ctypes
import os

LIB_PATH = os.path.dirname(__file__)

class CryptoBridge:
    def __init__(self):
        # Assume compiled Rust library as crypto.dll/so/dylib
        self.lib = ctypes.CDLL(os.path.join(LIB_PATH, 'crypto.so'))
        self.lib.hash_vote.argtypes = [ctypes.c_char_p]
        self.lib.hash_vote.restype = ctypes.c_char_p
        self.lib.sign_vote.argtypes = [ctypes.c_char_p]
        self.lib.sign_vote.restype = ctypes.c_char_p

    def hash_vote(self, vote_data: str) -> str:
        return self.lib.hash_vote(vote_data.encode('utf-8')).decode('utf-8')

    def sign_vote(self, vote_hash: str) -> str:
        return self.lib.sign_vote(vote_hash.encode('utf-8')).decode('utf-8')
