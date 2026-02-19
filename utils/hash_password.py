from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

hash = PasswordHasher()

def hash_password(password:str):
    return hash.hash(password)

def verify_password(hashed_password:str, plain_password:str):
    try:
        return hash.verify(hashed_password, plain_password)
    except VerifyMismatchError:
        return False