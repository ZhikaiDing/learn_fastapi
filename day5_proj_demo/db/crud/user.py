from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from db.models import User
from schemas.user_schema import UserRegister
from core.security import get_password_hash


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """根据邮箱查询用户，注册时用来判断邮箱是否已被占用、登录时查找用户"""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """通过用户id查询用户"""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserRegister) -> User:
    """新建用户：接收注册schema，密码哈希后存入数据库"""
    hashed_pw = get_password_hash(user_in.password)
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise
    await db.refresh(db_user)
    return db_user

