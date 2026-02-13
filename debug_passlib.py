from passlib.context import CryptContext
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

try:
    password = "testpassword123"
    print(f"Password length: {len(password)}")
    print(f"Hashing password using passlib: {password}")
    hashed = pwd_context.hash(password)
    print(f"Hashed: {hashed}")
except Exception as e:
    print(f"Passlib Error: {e}")

try:
    print(f"Hashing using bcrypt directly")
    salt = bcrypt.gensalt()
    hashed_bcrypt = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(f"Bcrypt Hashed: {hashed_bcrypt}")
except Exception as e:
    print(f"Bcrypt Error: {e}")
