"""
Security primitives and encryption
"""

import base64
import hashlib
from typing import bytes, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.backends import default_backend

def generate_key(message: str, private_key: bytes) -> str:
    """Generate digital signature for message"""
    # Simple HMAC-based signature for compatibility
    signature = hashlib.sha256(message.encode() + private_key).digest()
    return base64.b64encode(signature).decode()

def verify_signature(message: str, signature: str, public_key: bytes) -> bool:
    """Verify message signature"""
    expected = hashlib.sha256(message.encode() + public_key).digest()
    actual = base64.b64decode(signature.encode())
    return expected == actual

def encrypt_message(message: str, key: bytes) -> bytes:
    """Encrypt message with Fernet"""
    cipher = Fernet(key)
    encrypted = cipher.encrypt(message.encode())
    return encrypted

def decrypt_message(encrypted_data: bytes, key: bytes) -> str:
    """Decrypt message with Fernet"""
    cipher = Fernet(key)
    decrypted = cipher.decrypt(encrypted_data)
    return decrypted.decode()

def generate_rsa_keypair() -> tuple:
    """Generate RSA keypair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key

def serialize_private_key(private_key: rsa.RSAPrivateKey) -> bytes:
    """Serialize private key to PEM format"""
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

def serialize_public_key(public_key: rsa.RSAPublicKey) -> bytes:
    """Serialize public key to PEM format"""
    return public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )

def load_private_key(pem_bytes: bytes) -> rsa.RSAPrivateKey:
    """Load private key from PEM bytes"""
    return serialization.load_pem_private_key(
        pem_bytes,
        password=None,
        backend=default_backend()
    )

def load_public_key(pem_bytes: bytes) -> rsa.RSAPublicKey:
    """Load public key from PEM bytes"""
    return serialization.load_pem_public_key(
        pem_bytes,
        backend=default_backend()
    )

def sign_message(message: str, private_key: rsa.RSAPrivateKey) -> bytes:
    """Sign message with RSA"""
    return private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

def verify_rsa_signature(message: str, signature: bytes, public_key: rsa.RSAPublicKey) -> bool:
    """Verify RSA signature"""
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False
