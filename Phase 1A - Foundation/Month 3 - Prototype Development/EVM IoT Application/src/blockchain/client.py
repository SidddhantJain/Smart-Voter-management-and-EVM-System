"""
Blockchain Client for VoteGuard Pro EVM
Language: Python (gRPC/REST placeholder)
Handles: Secure connection and transaction submission to blockchain
"""


from .crypto_bridge import CryptoBridge
from web3 import Web3

class BlockchainClient:
    def __init__(self):
        self.crypto = CryptoBridge()
        self.web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))  # Replace with actual blockchain node URL
        if not self.web3.isConnected():
            raise ConnectionError("[BC] Unable to connect to the blockchain network.")
        self.contract_address = Web3.toChecksumAddress("0xYourContractAddress")  # Replace with actual contract address
        self.contract_abi = []  # Replace with actual contract ABI
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.contract_abi)

    def connect(self):
        print("[BC] Connected to blockchain network.")

    def submit_vote(self, candidate):
        print(f"[BC] Submitting vote for {candidate} to local backend (blockchain logic inactive)...")
        vote_hash = self.crypto.hash_vote(candidate)
        signature = self.crypto.sign_vote(vote_hash)
        print(f"[BC] Vote hash: {vote_hash}")
        print(f"[BC] Signature: {signature}")

        # Simulate local backend storage
        print("[BC] Storing vote locally for now.")
        return {
            "status": "success",
            "vote_hash": vote_hash,
            "signature": signature
        }

    def generate_keys(self):
        secret_key, public_key = self.crypto.generate_keypair()
        print(f"[BC] Generated keys: Secret Key: {secret_key}, Public Key: {public_key}")
        return secret_key, public_key

    def verify_vote(self, public_key, vote_hash, signature):
        is_valid = self.crypto.verify_signature(public_key, vote_hash, signature)
        print(f"[BC] Signature verification result: {is_valid}")
        return is_valid
