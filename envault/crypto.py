"""Encryption and decryption utilities for envault using AES-GCM."""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


SALT_SIZE = 16
NONCE_SIZE = 12
KEY_SIZE = 32
MIN_PAYLOAD_SIZE = SALT_SIZE + NONCE_SIZE


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit key from a password using scrypt."""
    kdf = Scrypt(salt=salt, length=KEY_SIZE, n=2**14, r=8, p=1)
    return kdf.derive(password.encode())


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt plaintext with a password. Returns a base64-encoded token."""
    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    payload = salt + nonce + ciphertext
    return base64.urlsafe_b64encode(payload).decode()


def decrypt(token: str, password: str) -> str:
    """Decrypt a base64-encoded token with a password. Returns plaintext."""
    try:
        payload = base64.urlsafe_b64decode(token.encode())
    except Exception as exc:
        raise ValueError("Invalid token format.") from exc

    if len(payload) < MIN_PAYLOAD_SIZE:
        raise ValueError(
            f"Token is too short to be valid (got {len(payload)} bytes, "
            f"expected at least {MIN_PAYLOAD_SIZE})."
        )

    salt = payload[:SALT_SIZE]
    nonce = payload[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    ciphertext = payload[SALT_SIZE + NONCE_SIZE:]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    except Exception as exc:
        raise ValueError("Decryption failed. Wrong password or corrupted data.") from exc

    return plaintext.decode()
