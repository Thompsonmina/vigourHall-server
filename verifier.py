import secrets
import hashlib
import base64

def generate_code_verifier() -> str:
    token = secrets.token_urlsafe(96)  # Generates a random URL-safe text string
    while len(token) < 43:
        token += secrets.token_urlsafe(len(token))
    
    return token[:128]  # Truncate to 128 characters if longer



def generate_code_challenge(code_verifier: str) -> str:
    # Create a SHA-256 hash of the code_verifier
    sha256_hash = hashlib.sha256(code_verifier.encode())
    # Get the digest as bytes
    digest_bytes = sha256_hash.digest()
    # Base64 encode the bytes
    challenge = base64.urlsafe_b64encode(digest_bytes).decode().replace("=", "")
    return challenge

def generate_state() -> str:
    return secrets.token_urlsafe(16)  # Generates a 16-byte long URL-safe text string


if __name__ == "__main__":
    code_verifier = generate_code_verifier()
    print(code_verifier)

    code_challenge = generate_code_challenge(code_verifier)
    print(code_challenge)