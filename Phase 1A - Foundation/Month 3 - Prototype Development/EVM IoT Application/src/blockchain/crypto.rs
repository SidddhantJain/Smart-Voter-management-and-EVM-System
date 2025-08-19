// Rust cryptographic module for VoteGuard Pro EVM
// Handles secure hashing, signing, and verification
use sha2::{Sha256, Digest};

pub fn hash_vote(data: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    let result = hasher.finalize();
    hex::encode(&result)
}

// TODO: Add digital signature and verification functions
