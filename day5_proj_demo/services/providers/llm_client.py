from openai import OpenAI, AsyncOpenAI
from db.models import UserModelConfig
from typing import List, Dict, AsyncGenerator

from core.security import decrypt_api_key

async def call_llm(
    model_config: UserModelConfig,
    sys_prompt: str,
    history_messages: List[Dict[str, str]]
) -> str:
    # 解密，拿到原始明文api key
    plain_api_key = decrypt_api_key(model_config.hashed_model_api_key)

    client = OpenAI(
        api_key=plain_api_key,
        base_url=model_config.model_type # 例如 "https://api.deepseek.com/v1"
    )

    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(history_messages)

    resp = client.chat.completions.create(
        model=model_config.model_name,
        messages=messages,
        temperature=0.7
    )
    return resp.choices[0].message.content.strip()

async def stream_llm(
    model_config: UserModelConfig,
    sys_prompt: str,
    history_messages: List[Dict[str, str]]
) -> AsyncGenerator[str, None]:
    """异步生成器，async yield 文本块"""
    plain_api_key = decrypt_api_key(model_config.hashed_model_api_key)

    client = AsyncOpenAI(
        api_key=plain_api_key,
        base_url=model_config.model_type
    )

    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(history_messages)

    stream = await client.chat.completions.create(
        model=model_config.model_name,
        messages=messages,
        temperature=0.7,
        stream=True
    )
    full_content = ""
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            full_content += text
            yield text
    yield f"__END__:{full_content}"
