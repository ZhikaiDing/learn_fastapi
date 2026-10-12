from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# ========== Conversation Schema ==========
class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100, description="对话标题")
    sys_prompt: str = Field(description="会话级系统提示词")

class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    sys_prompt: Optional[str] = None

class ConversationOut(BaseModel):
    id: int
    title: str
    sys_prompt: str
    created_at: datetime
    update_at: datetime

    class Config:
        from_attributes = True

# ========== Message Schema ==========
class MessageCreate(BaseModel):
    model_cfg_id: int
    content: str = Field(description="用户输入内容")

class MessageOut(BaseModel):
    id: int
    conversation_id: int
    model_cfg_id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# 发送消息并获取LLM回复的响应
class ChatResponse(BaseModel):
    user_msg: MessageOut
    ai_msg: MessageOut
