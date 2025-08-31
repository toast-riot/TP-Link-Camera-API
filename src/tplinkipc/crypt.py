import hashlib
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

def md5_auth_pwd(password: str, salt: str) -> str: # original: md5AuthPwd
    return hashlib.md5((salt + password).encode()).hexdigest().upper()

def rsa_encrypt(data: str, pubkey_pem: str) -> str:
    public_key = serialization.load_pem_public_key(pubkey_pem.encode())
    encrypted = public_key.encrypt(data.encode(), padding.PKCS1v15())
    return base64.b64encode(encrypted).decode()

def make_pem(key: str) -> str:
    return f"-----BEGIN PUBLIC KEY-----\n{key}\n-----END PUBLIC KEY-----"