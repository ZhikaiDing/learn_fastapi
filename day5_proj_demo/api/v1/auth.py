from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status

from db.crud.user import get_user_by_email, create_user
from schemas.user_schema import UserRegister, UserLogin, TokenResponse
from core.security import verify_password, create_access_token
from core.settings import settings
from api.deps_base import DbSession
from api.deps import CurUser

router = APIRouter(tags=["认证"], prefix="/auth")

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    *,
    user_in: UserRegister,
    db: DbSession
):
    """用户注册接口 POST /api/v1/auth/register"""
    # 检查邮箱是否已经存在
    db_user = get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    # 创建新用户
    new_user = create_user(db, obj_in=user_in)
    return {
        "msg": "注册成功",
        "user_id": new_user.id,
        "email": new_user.email
    }


@router.post("/login", response_model=TokenResponse)
def login(
    login_in: UserLogin,
    db: DbSession,
    # form_data: LoginData
):
    """
    用户登录 POST /api/v1/auth/login
    OAuth2 标准表单：username 传邮箱，password传密码
    返回 access_token
    """
    # 这里OAuth2的表单字段叫username，我们用来存用户邮箱
    user = get_user_by_email(db, email=login_in.email) # email=form_data.username
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    # 校验密码
    if not verify_password(login_in.password, user.hashed_password): # form_data.password
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )
    # 生成JWT token，设置过期时间
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},  # sub存放用户id，标准JWT声明
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user  # 这里user是SQLAlchemy ORM对象！
        # 因为`UserResponse`里面设置了 `from_attributes=True`，Pydantic 会自动从 ORM 对象读取属性，转换成 UserResponse
    }

@router.get("/me")
async def read_user_info(current_user: CurUser):
    # 只要进到这个函数，说明用户已经登录成功
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }
