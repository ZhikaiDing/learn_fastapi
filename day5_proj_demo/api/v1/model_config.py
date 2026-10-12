from fastapi import APIRouter, HTTPException, status
from typing import List

from schemas.model_schema import (
    UserModelConfigCreate,
    UserModelConfigUpdate,
    UserModelConfigResponse
)
from db.crud import model_config as crud_mc
from core.security import decrypt_api_key, mask_api_key

from api.deps_base import DbSession
from api.deps import CurUser

router = APIRouter(prefix="/model_config", tags=["用户模型API配置"])

# 新建模型配置
@router.post("/", response_model=UserModelConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_model_config(
    *,
    db: DbSession,
    config_in: UserModelConfigCreate,
    current_user: CurUser
):
    db_cfg = await crud_mc.create_model_config(db=db, obj_in=config_in, user_id=current_user.id)
    return {
        "id": db_cfg.id,
        "config_name": db_cfg.config_name,
        "model_type": db_cfg.model_type,
        "model_name": db_cfg.model_name,
        "model_api_key_mask": mask_api_key(config_in.model_api_key),
        "created_at": db_cfg.created_at
    }

# 获取当前用户全部模型配置列表
@router.get("/", response_model=List[UserModelConfigResponse])
async def list_model_configs(
    db: DbSession,
    current_user: CurUser
):
    cfg_list = await crud_mc.get_user_model_configs(db=db, user_id=current_user.id)
    resp_list = []
    for item in cfg_list:
        masked_api_key = mask_api_key(decrypt_api_key(item.hashed_model_api_key))
        resp_list.append({
            "id": item.id,
            "config_name": item.config_name,
            "model_type": item.model_type,
            "model_name": item.model_name,
            "model_api_key_mask": masked_api_key,
            "created_at": item.created_at
        })
    return resp_list

# 获取单条模型配置
@router.get("/{config_id}", response_model=UserModelConfigResponse)
async def get_one_config(
    config_id: int,
    db: DbSession,
    current_user: CurUser
):
    cfg = await crud_mc.get_model_config_by_id(db=db, config_id=config_id, user_id=current_user.id)
    if not cfg:
        raise HTTPException(status_code=404, detail="模型配置不存在或无权限")
    masked_api_key = mask_api_key(decrypt_api_key(cfg.hashed_model_api_key))
    return {
        "id": cfg.id,
        "config_name": cfg.config_name,
        "model_type": cfg.model_type,
        "model_name": cfg.model_name,
        "model_api_key_mask": masked_api_key,
        "created_at": cfg.created_at
    }

# 更新模型配置
@router.put("/{config_id}", response_model=UserModelConfigResponse)
async def update_config(
    config_id: int,
    config_in: UserModelConfigUpdate,
    db: DbSession,
    current_user: CurUser
):
    cfg = await crud_mc.get_model_config_by_id(db=db, config_id=config_id, user_id=current_user.id)
    if not cfg:
        raise HTTPException(status_code=404, detail="模型配置不存在或无权限")
    updated_cfg = await crud_mc.update_model_config(db=db, db_obj=cfg, obj_in=config_in)
    return {
        "id": updated_cfg.id,
        "config_name": updated_cfg.config_name,
        "model_type": updated_cfg.model_type,
        "model_name": updated_cfg.model_name,
        "model_api_key_mask": mask_api_key(config_in.model_api_key),
        "created_at": updated_cfg.created_at
    }


# 删除模型配置
@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_config(
    config_id: int,
    db: DbSession,
    current_user: CurUser
):
    cfg = await crud_mc.get_model_config_by_id(db=db, config_id=config_id, user_id=current_user.id)
    if not cfg:
        raise HTTPException(status_code=404, detail="模型配置不存在或无权限")
    await crud_mc.delete_model_config(db=db, db_obj=cfg)
    return
