from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi import BackgroundTasks
from sqlalchemy import select
import json
from typing import List

from db.models import User, UserModelConfig
from schemas.chat_schema import (
    ConversationCreate, ConversationOut, ConversationUpdate,
    MessageCreate, ChatResponse
)
from db.crud.conversation import (
    create_conversation, get_conversation_by_id,
    list_conversations, update_conversation, delete_conversation
)
from db.crud.message import create_message, get_messages_by_conversation_id
from services.providers.llm_client import call_llm, stream_llm

from api.deps_base import DbSession
from api.deps import CurUser

router = APIRouter(prefix="/conversations", tags=["对话管理"])

# 1. 创建会话
@router.post("/", response_model=ConversationOut)
async def create_conv(
    *,
    db: DbSession,
    current_user: CurUser,
    conv_in: ConversationCreate
):
    return await create_conversation(db, obj_in=conv_in, user_id=current_user.id)

# 2. 获取会话列表
@router.get("/", response_model=List[ConversationOut])
async def list_conv(
    db: DbSession,
    current_user: CurUser,
    skip:int=0, limit:int=50
):
    return await list_conversations(db, user_id=current_user.id, skip=skip, limit=limit)

# 3. 获取会话详情（会话信息 + 历史消息）
@router.get("/{conv_id}")
async def get_conv_detail(
    *,
    db: DbSession,
    current_user: CurUser,
    conv_id: int
):
    conv = await get_conversation_by_id(db, conv_id=conv_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    msgs = await get_messages_by_conversation_id(db, conv_id)
    return {
        "conversation": conv,
        "messages": msgs
    }

# 4. 更新会话标题/sys_prompt
@router.patch("/{conv_id}", response_model=ConversationOut)
async def update_conv(
    *,
    db: DbSession,
    current_user: CurUser,
    conv_id: int,
    conv_in: ConversationUpdate
):
    conv = await get_conversation_by_id(db, conv_id=conv_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    return await update_conversation(db, db_obj=conv, obj_in=conv_in)

# 5. 删除会话
@router.delete("/{conv_id}")
async def delete_conv(
    *,
    db: DbSession,
    current_user: CurUser,
    conv_id: int
):
    ok = await delete_conversation(db, conv_id=conv_id, user_id=current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"msg": "删除成功"}

# ===================== 聊天核心接口：发送消息 =====================
@router.post("/{conv_id}/chat", response_model=ChatResponse)
async def chat_send_message(
    *,
    db: DbSession,
    current_user: CurUser,
    conv_id: int,
    msg_in: MessageCreate
):
    # 1. 校验会话归属当前用户
    conv = await get_conversation_by_id(db, conv_id=conv_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 2. 校验model_cfg_id归属当前用户，防止越权使用别人密钥
    stmt_cfg = select(UserModelConfig).where(
        UserModelConfig.id == msg_in.model_cfg_id,
        UserModelConfig.user_id == current_user.id
    )
    res_cfg = await db.execute(stmt_cfg)
    model_cfg = res_cfg.scalar_one_or_none()
    if not model_cfg:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    # 3. 保存用户消息
    user_msg = await create_message(
        db,
        conversation_id=conv.id,
        model_cfg_id=msg_in.model_cfg_id,
        role="user",
        content=msg_in.content
    )

    # 4. 获取历史消息，组装给LLM
    history_db_msgs = await get_messages_by_conversation_id(db, conv_id=conv.id)
    history = []
    for m in history_db_msgs:
        history.append({"role": m.role, "content": m.content})

    # 5. 调用LLM
    ai_content = await call_llm(
        model_config=model_cfg,
        sys_prompt=conv.sys_prompt,
        history_messages=history
    )

    # 6. 保存AI回复消息
    ai_msg = await create_message(
        db,
        conversation_id=conv.id,
        model_cfg_id=msg_in.model_cfg_id,
        role="assistant",
        content=ai_content
    )

    return ChatResponse(user_msg=user_msg, ai_msg=ai_msg)

# 新增流式聊天接口
# 示例片段
@router.post("/{conv_id}/stream-chat")
async def chat_stream(
    *,
    db: DbSession,
    current_user: CurUser,
    conv_id: int,
    msg_in: MessageCreate
):
    # 这里加 await
    conv = await get_conversation_by_id(db, conv_id=conv_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")

    # 查询model_cfg也要改成select + await
    stmt_cfg = select(UserModelConfig).where(
        UserModelConfig.id == msg_in.model_cfg_id,
        UserModelConfig.user_id == current_user.id
    )
    res_cfg = await db.execute(stmt_cfg)
    model_cfg = res_cfg.scalar_one_or_none()
    if not model_cfg:
        raise HTTPException(status_code=404, detail="模型配置不存在")

    # 保存用户消息，加 await
    user_msg = await create_message(
        db,
        conversation_id=conv.id,
        model_cfg_id=msg_in.model_cfg_id,
        role="user",
        content=msg_in.content
    )

    # 获取历史消息 await
    history_db_msgs = await get_messages_by_conversation_id(db, conv_id=conv.id)
    history = []
    for m in history_db_msgs:
        history.append({"role": m.role, "content": m.content})

    bg_tasks = BackgroundTasks()

    async def save_ai_message(full_text: str):
        await create_message(
            db,
            conversation_id=conv.id,
            model_cfg_id=msg_in.model_cfg_id,
            role="assistant",
            content=full_text
        )

    async def sse_generator_bg():
        ai_full_text = ""
        try:
            async for chunk in stream_llm(model_cfg, conv.sys_prompt, history):
                if chunk.startswith("__END__:"):
                    ai_full_text = chunk.replace("__END__:", "")
                    continue
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            # 流结束，注册后台任务保存消息
            # ✅ 这里注意：在异步生成器内部，不能直接使用 db 会话！
            # 【重大坑】sse_generator 执行时机是在响应流输出阶段，请求生命周期可能已经结束，db会话会被回收！
            # 方案：使用后台任务 BackgroundTasks，在流结束后执行保存AI消息
            bg_tasks.add_task(save_ai_message, ai_full_text)
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    resp = StreamingResponse(
        sse_generator_bg(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Content-Type-Options": "nosniff"
        }
    )
    resp.background = bg_tasks
    return resp
