from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

KEY_SIZE = 32      # 256-bit key
NONCE_SIZE = 12     # 96-bit nonce, standard for GCM
TAG_SIZE = 16        # 128-bit auth tag


def generate_key() -> bytes:
    """Generate a random AES-256 key."""
    return get_random_bytes(KEY_SIZE)


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """
    Encrypt bytes with AES-256-GCM.
    Output format: nonce (12 bytes) + tag (16 bytes) + ciphertext
    """
    nonce = get_random_bytes(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return nonce + tag + ciphertext


def decrypt_data(encrypted_blob: bytes, key: bytes) -> bytes:
    """
    Decrypt bytes produced by encrypt_data.
    Raises ValueError if the key is wrong or data was tampered with.
    """
    nonce = encrypted_blob[:NONCE_SIZE]
    tag = encrypted_blob[NONCE_SIZE:NONCE_SIZE + TAG_SIZE]
    ciphertext = encrypted_blob[NONCE_SIZE + TAG_SIZE:]

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    return plaintext


if __name__ == "__main__":
    # Standalone self-test
    sample = b"This is a test image's worth of bytes."
    key = generate_key()

    encrypted = encrypt_data(sample, key)
    decrypted = decrypt_data(encrypted, key)

    print("Key (hex):", key.hex())
    print("Original: ", sample)
    print("Decrypted:", decrypted)
    print("Match:", sample == decrypted)