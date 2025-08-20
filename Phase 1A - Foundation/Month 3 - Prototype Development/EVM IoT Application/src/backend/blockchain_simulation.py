"""
Blockchain Simulation for VoteGuard Pro EVM
Language: Python
Handles: Simulated blockchain-based vote storage
"""
import hashlib
import json
from time import time

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_votes = []
        self.create_block(previous_hash='1', proof=100)  # Genesis block

    def create_block(self, proof, previous_hash):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'votes': self.current_votes,
            'proof': proof,
            'previous_hash': previous_hash,
        }
        self.current_votes = []
        self.chain.append(block)
        return block

    def add_vote(self, voter_id, candidate_id):
        self.current_votes.append({
            'voter_id': voter_id,
            'candidate_id': candidate_id,
        })
        return self.last_block['index'] + 1

    def hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def valid_proof(self, last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @property
    def last_block(self):
        return self.chain[-1]

if __name__ == "__main__":
    blockchain = Blockchain()
    blockchain.add_vote("123456789012", "Candidate A")
    blockchain.add_vote("987654321098", "Candidate B")
    proof = blockchain.proof_of_work(blockchain.last_block['proof'])
    blockchain.create_block(proof, blockchain.hash(blockchain.last_block))
    print("Blockchain:", json.dumps(blockchain.chain, indent=4))
