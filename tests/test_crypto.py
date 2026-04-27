"""Unit tests for envault.crypto module."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-password"
PLAINTEXT = "HELLO=world\nAPI_KEY=abc123"


def test_encrypt_returns_string():
    token = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_decrypt_roundtrip():
    token = encrypt(PLAINTEXT, PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == PLAINTEXT


def test_encrypt_produces_different_tokens():
    token1 = encrypt(PLAINTEXT, PASSWORD)
    token2 = encrypt(PLAINTEXT, PASSWORD)
    # Random salt and nonce mean tokens differ each time
    assert token1 != token2


def test_decrypt_wrong_password_raises():
    token = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-password")


def test_decrypt_invalid_token_raises():
    with pytest.raises(ValueError):
        decrypt("not-a-valid-token!!", PASSWORD)


def test_decrypt_truncated_token_raises():
    with pytest.raises(ValueError):
        decrypt("dG9vc2hvcnQ=", PASSWORD)  # base64 for "tooshort"


def test_encrypt_empty_string():
    token = encrypt("", PASSWORD)
    assert decrypt(token, PASSWORD) == ""


def test_encrypt_unicode():
    text = "SECRET=caf\u00e9"
    token = encrypt(text, PASSWORD)
    assert decrypt(token, PASSWORD) == text
