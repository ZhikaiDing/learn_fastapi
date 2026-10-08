from fastapi import Depends
# from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Annotated

from db.session import get_db

DbSession = Annotated[Session, Depends(get_db)]
# LoginData = Annotated[OAuth2PasswordRequestForm, Depends()]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
JWTtoken = Annotated[str, Depends(oauth2_scheme)]
