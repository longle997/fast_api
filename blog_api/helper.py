from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm.session import Session
from jose import JWTError, jwt

from .services import get_db
from .users.users_services import get_single_user
from .users.send_email_services import Envs
from fastapi.templating import Jinja2Templates
# initialize authication
# The oauth2_scheme variable is an instance of OAuth2PasswordBearer, but it is also a "callable".
# So, it can be used with Depends.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login", auto_error=False)

SECRET_KEY = Envs.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

templates = Jinja2Templates(directory="blog_api/static/templates")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_name : str = payload.get("sub")
        if not user_name:
            raise CREDENTIAL_EXCEPTION

        user = await get_single_user(db, user_name)
        if not user:
            raise CREDENTIAL_EXCEPTION

    except JWTError:
        raise CREDENTIAL_EXCEPTION

    return user


async def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt
