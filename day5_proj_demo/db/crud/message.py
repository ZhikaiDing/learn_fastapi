from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import Message

async def create_message(
    db: AsyncSession,
    *,
    conversation_id: int,
    model_cfg_id: int,
    role: str,
    content: str
):
    db_obj = Message(
        conversation_id=conversation_id,
        model_cfg_id=model_cfg_id,
        role=role,
        content=content
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def get_messages_by_conversation_id(db: AsyncSession, conv_id: int):
    stmt = select(Message)\
        .where(Message.conversation_id == conv_id)\
        .order_by(Message.created_at.asc())
    result = await db.execute(stmt)
    return result.scalars().all()
