import jwt
from jwt import InvalidTokenError, ExpiredSignatureError, DecodeError
from datetime import datetime, timedelta
from config.setting import Setting

setting = Setting()

SECRETCODE = setting.jwtsecretcode
ALGORITHM = setting.algorithm

def create_access_token(data: dict, mins=15):
    to_encode = data.copy()
    expiry = datetime.utcnow() + timedelta(minutes=mins)
    to_encode.update({"exp": expiry})
    return jwt.encode(to_encode, SECRETCODE, algorithm=ALGORITHM)

def create_refresh_token(data: dict, days=7):
    to_encode = data.copy()
    expiry = datetime.utcnow() + timedelta(days=days)
    to_encode.update({"exp": expiry})
    return jwt.encode(to_encode, SECRETCODE, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRETCODE, algorithms=[ALGORITHM])
    except (InvalidTokenError, DecodeError, ExpiredSignatureError):
        return None