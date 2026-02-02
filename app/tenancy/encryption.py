from cryptography.fernet import Fernet
from app.config import settings

class PasswordEncryption:
    """Encrypt/decrypt tenant database passwords"""
    
    def __init__(self):
        # In production, store this in a secure vault (AWS Secrets Manager, etc.)
        self.fernet = Fernet(settings.TENANT_PASSWORD_ENCRYPTION_KEY.encode())
    
    def encrypt(self, password: str) -> str:
        """Encrypt a password"""
        encrypted = self.fernet.encrypt(password.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_password: str) -> str:
        """Decrypt a password"""
        decrypted = self.fernet.decrypt(encrypted_password.encode())
        return decrypted.decode()


# Global encryption instance
password_encryption = PasswordEncryption()


def encrypt_password(password: str) -> str:
    """Helper to encrypt password"""
    return password_encryption.encrypt(password)


def decrypt_password(encrypted: str) -> str:
    """Helper to decrypt password"""
    return password_encryption.decrypt(encrypted)
