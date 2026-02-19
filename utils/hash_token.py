import hashlib

def hash_tokens(token:str):
    return hashlib.sha256(token.encode()).hexdigest()