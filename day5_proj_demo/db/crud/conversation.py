from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.models import Conversation
from schemas.chat_schema import ConversationCreate, ConversationUpdate

async def create_conversation(db: AsyncSession, *, obj_in: ConversationCreate, user_id: int):
    db_obj = Conversation(
        user_id=user_id,
        title=obj_in.title,
        sys_prompt=obj_in.sys_prompt
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_conversation_by_id(db: AsyncSession, conv_id: int, user_id: int):
    stmt = select(Conversation).where(
        Conversation.id == conv_id,
        Conversation.user_id == user_id
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def list_conversations(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50):
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_conversation(db: AsyncSession, *, db_obj: Conversation, obj_in: ConversationUpdate):
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    # 更新时间戳
    db_obj.update_at = func.now()
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_conversation(db: AsyncSession, *, conv_id: int, user_id: int):
    db_obj = await get_conversation_by_id(db, conv_id, user_id)
    if not db_obj:
        return None
    await db.delete(db_obj)
    await db.commit()
    return True
