from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from sqlalchemy.orm.session import Session
from jose import JWTError, jwt

from . import services

# initialize authication
# The oauth2_scheme variable is an instance of OAuth2PasswordBearer, but it is also a "callable".
# So, it can be used with Depends.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

SECRET_KEY = "0cd0a267e9d2c1e6c46f66cb7468eaf117052763531f9ac45a10989968f6ee9f"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(services.get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_name : str = payload.get("sub")
        if not user_name:
            raise CREDENTIAL_EXCEPTION

        user = services.get_single_user(db, user_name)
        if not user:
            raise CREDENTIAL_EXCEPTION

    except JWTError:
        raise CREDENTIAL_EXCEPTION

    return user


def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt