import logging
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import Depends
from fastapi import security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi import HTTPException, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm.session import Session
from jose import JWTError, jwt
from pydantic import BaseModel, ValidationError

from .services import get_db
from .users.users_services import get_single_user
from .users.send_email_services import Envs

# initialize authication
# The oauth2_scheme variable is an instance of OAuth2PasswordBearer, but it is also a "callable".
# So, it can be used with Depends.
# by adding scopes parameter, we affect to OAuth2PasswordRequestForm from user login api
# The scopes parameter receives a dict with each scope as a key and the description as the
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="users/login",
    auto_error=False
)

logger = logging.getLogger(__name__)

SECRET_KEY = Envs.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

templates = Jinja2Templates(directory="blog_api/static/templates")

# The important and "magic" thing here is that get_current_user will have a different list of scopes to check for each path operation.
# All depending on the scopes declared in each path operation and each dependency in the dependency tree for that specific path operation.
async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)):

    # security_scopes.scopes is what we declare at api
    # for example: current_user: User_db = Security(get_current_user, scopes=["ahihi"])
    # in this case security_scopes.scopes will be "ahihi"
    # The security_scopes object (of class SecurityScopes) also provides a scope_str attribute with a single string, containing those scopes separated by spaces (we are going to use it).
    if security_scopes.scopes:
        authenticate_value = f'Available Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f'Bearer'

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_name : str = payload.get("sub")
        if not user_name:
            raise credentials_exception

        # token_scopes is that we get from token, this token was create by login_for_access_token api
        token_scopes = payload.get("scopes", [])

        token_data = TokenData(scopes=token_scopes, username=user_name)
    except (JWTError, ValidationError):
        raise credentials_exception

    user = await get_single_user(db, user_name)
    if not user:
        raise credentials_exception

    # we use security_scopes.scopes, that contains a list with all these scopes as str.
    for scope in security_scopes.scopes:
        if scope in token_data.scopes:
            break
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not enough permissions",
            headers={"WWW-Authenticate": authenticate_value},
        )

    return user


# this access token doesn't saved anywhere, all data need to validate are inside token itself
# expire is include inside token and OAuth2PasswordBearer will validate it
async def create_access_token(data: dict, expire_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)

    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encode_jwt


# async def test_scope(scopes: SecurityScopes, token = Depends(oauth2_scheme_2)):
async def test_scope(scopes: SecurityScopes, input_scopes: str):
    if input_scopes == scopes.scopes[0]:
        return scopes.scopes
    return None