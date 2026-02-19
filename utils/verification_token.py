import secrets

def generate_verification_token(length=6):
    return "".join(str(secrets.randbelow(10)) for _ in range(length))