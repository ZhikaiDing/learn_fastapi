from sqlalchemy.ext.asyncio import AsyncSession
from db.models import UserModelConfig
from schemas.model_schema import UserModelConfigCreate, UserModelConfigUpdate
from sqlalchemy import select
from typing import List, Optional
from core.security import encrypt_api_key


# 创建一条用户模型配置
async def create_model_config(
    db: AsyncSession,
    obj_in: UserModelConfigCreate,
    user_id: int
) -> UserModelConfig:
    db_obj = UserModelConfig(
        user_id=user_id,
        config_name=obj_in.config_name,
        model_type=obj_in.model_type,
        model_name=obj_in.model_name,
        hashed_model_api_key=encrypt_api_key(obj_in.model_api_key)
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


# 查询单个配置（必须校验归属user_id，防止越权）
async def get_model_config_by_id(
    db: AsyncSession,
    config_id: int,
    user_id: int
) -> Optional[UserModelConfig]:
    stmt = select(UserModelConfig).where(
        UserModelConfig.id == config_id,
        UserModelConfig.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# 获取当前用户所有的模型配置列表
async def get_user_model_configs(
    db: AsyncSession,
    user_id: int
) -> List[UserModelConfig]:
    stmt = select(UserModelConfig).where(UserModelConfig.user_id == user_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


def update_model_config(
    db: AsyncSession,
    db_obj: UserModelConfig,
    obj_in: UserModelConfigUpdate
) -> UserModelConfig:
    """⚠️ 注意：这里忘记改成async，下面已经修正"""
    pass

async def update_model_config(
    db: AsyncSession,
    db_obj: UserModelConfig,
    obj_in: UserModelConfigUpdate
) -> UserModelConfig:
    # 只拿到前端有传入的字段
    update_data = obj_in.model_dump(exclude_unset=True)
    # 如果前端提交了 model_api_key，单独处理加密
    if "model_api_key" in update_data:
        plain_api_key = update_data.pop("model_api_key")
        # 如果不为空字符串，加密；如果传空可以按需加校验
        if plain_api_key:
            encrypted_key = encrypt_api_key(plain_api_key)
            db_obj.hashed_model_api_key = encrypted_key
    # 剩下普通字段直接循环赋值（config_name / model_type / model_name）
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# 删除一条模型配置
async def delete_model_config(
    db: AsyncSession,
    db_obj: UserModelConfig
) -> None:
    await db.delete(db_obj)
    await db.commit()
