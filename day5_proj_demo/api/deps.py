from fastapi import Depends
from typing import Annotated

from db.models import User
from core.security import get_current_user

CurUser = Annotated[User, Depends(get_current_user)]
