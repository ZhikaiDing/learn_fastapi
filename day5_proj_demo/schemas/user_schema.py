from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# 注册的 post请求
class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, description="用户名，3~50字符")
    password: str = Field(min_length=6, max_length=100, description="密码至少6位")

# 登录的 post 请求
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100, description="密码至少6位")

# 登录成功的 响应
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str

    # 第三方登录 预留
    oauth_provider: Optional[str] = None
    oauth_id: Optional[int] = None

    # 可以直接把 SQLAlchemy User ORM 对象传给这个 Pydantic 模型，自动转成 json 返回，不用手动逐个赋值
    class Config:
        from_attributes = True

# 登录成功的 Token (返回 JWT 令牌 - 鉴权凭证)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
