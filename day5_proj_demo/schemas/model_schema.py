from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# 创建模型配置：前端POST提交用
class UserModelConfigCreate(BaseModel):
    config_name: str = Field(description="配置别名，例如：我的DeepSeek")
    model_type: str = Field(description="厂商类型，如 openai / deepseek / qwen")
    model_name: str = Field(description="模型名称，如 gpt-3.5-turbo")
    model_api_key: str = Field(description="用户自己的API Key")

# 更新模型配置
class UserModelConfigUpdate(BaseModel):
    config_name: Optional[str] = None
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    model_api_key: Optional[str] = None

# 返回给前端（⚠️ 关键：不返回完整明文apikey，只展示掩码）
class UserModelConfigResponse(BaseModel):
    id: int
    config_name: str
    model_type: str
    model_name: str
    # 掩码展示，不返回完整key！安全重点
    model_api_key_mask: str
    created_at: datetime

    class Config:
        from_attributes = True
