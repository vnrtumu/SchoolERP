#!/usr/bin/env python
"""
Generate Fernet encryption key for tenant password encryption.

Usage:
    python scripts/generate_key.py
"""
from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = Fernet.generate_key()
    print("\nGenerated Fernet encryption key:")
    print("="*60)
    print(key.decode())
    print("="*60)
    print("\nAdd this to your .env file as:")
    print(f"TENANT_PASSWORD_ENCRYPTION_KEY={key.decode()}")
    print()
