// Rust cryptographic module for VoteGuard Pro EVM
// Handles secure hashing, signing, and verification
use sha2::{Sha256, Digest};
use ed25519_dalek::{Keypair, PublicKey, SecretKey, Signature, Signer, Verifier};
use rand::rngs::OsRng;

pub fn hash_vote(data: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    let result = hasher.finalize();
    hex::encode(&result)
}

pub fn generate_keypair() -> (String, String) {
    let mut csprng = OsRng {};
    let keypair = Keypair::generate(&mut csprng);
    (
        hex::encode(keypair.secret.to_bytes()),
        hex::encode(keypair.public.to_bytes()),
    )
}

pub fn sign_vote(secret_key_hex: &str, vote_hash: &str) -> String {
    let secret_key_bytes = hex::decode(secret_key_hex).expect("Invalid secret key hex");
    let secret_key = SecretKey::from_bytes(&secret_key_bytes).expect("Invalid secret key");
    let public_key = PublicKey::from(&secret_key);
    let keypair = Keypair { secret: secret_key, public: public_key };
    let signature = keypair.sign(vote_hash.as_bytes());
    hex::encode(signature.to_bytes())
}

pub fn verify_signature(public_key_hex: &str, vote_hash: &str, signature_hex: &str) -> bool {
    let public_key_bytes = hex::decode(public_key_hex).expect("Invalid public key hex");
    let public_key = PublicKey::from_bytes(&public_key_bytes).expect("Invalid public key");
    let signature_bytes = hex::decode(signature_hex).expect("Invalid signature hex");
    let signature = Signature::from_bytes(&signature_bytes).expect("Invalid signature");
    public_key.verify(vote_hash.as_bytes(), &signature).is_ok()
}
