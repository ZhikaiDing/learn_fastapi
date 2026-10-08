from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import User
from schemas.user_schema import UserRegister
from core.security import get_password_hash

def get_user_by_email(db: Session, email: str) -> User | None:
    """根据邮箱查询用户，注册时用来判断邮箱是否已被占用、登录时查找用户"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    """通过用户id查询用户"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user_in: UserRegister) -> User:
    """新建用户：接收注册schema，密码哈希后存入数据库"""
    # 把前端传来的明文密码转为哈希
    hashed_pw = get_password_hash(user_in.password)
    # 构造ORM对象
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        # 唯一键冲突（邮箱重复），回滚，向上抛异常给接口层处理
        db.rollback()
        raise
    db.refresh(db_user)
    return db_user
