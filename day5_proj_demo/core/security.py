from datetime import datetime, timedelta, UTC
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import HTTPException, status

# 从settings读取配置，后面core/settings.py会读取.env
from core.settings import settings
from api.deps_base import DbSession, JWTtoken
from db.crud.user import get_user_by_id

# bcrypt密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """校验明文密码和数据库存储的哈希密码是否匹配"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """把明文密码计算成bcrypt哈希串"""
    return pwd_context.hash(password)


# JWT相关
class TokenData(BaseModel):
    """token里存放的数据payload模型，这里存user_id"""
    user_id: int | None = None


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    """生成JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        # 默认过期时间 15分钟
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(
    db: DbSession,
    token: JWTtoken
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证身份",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    return user
