from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import asyncio

token_time = 0.2

app = FastAPI()

# 鉴权
api_key_header = APIKeyHeader(name="LLM-API-KEY")
def check_api_key(api_key = Depends(api_key_header)):
    valid_keys = ["sk-abcd1234"]
    if api_key in valid_keys:
        return api_key
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad llm api key")
# 注: 假设一个应用，用户有自己的账号密码，又配置大模型的 api key，这里的鉴权是怎样的?
# 1. 用户账号
#    凭证：JWT / Session（你的系统颁发）
#    放在：`Authorization: Bearer <你的JWT>`
#    作用：确认这个请求是哪个登录用户发来的，拿到用户 ID，去数据库查出这个用户预先配置好的 LLM API Key。
# 2. 大模型 api key
#    后端内部发起 HTTP 请求调用大模型，在后端内部请求的 Header 带上用户的 LLM api key

class ChatReq(BaseModel):
    prompt:str
    is_stream:bool = False

async def call_llm_stream(prompt:str):
    content = "这是流式输出。"
    for c in content:
        await asyncio.sleep(token_time)
        yield f"data: {c}\n\n"

    yield f"data: [DONE]\n\n"

async def call_llm_full(prompt:str):
    content = "这是整体输出。"
    await asyncio.sleep(token_time * len(content))
    return content

# 注：只要函数体内出现 yield，它就变成异步生成器（async generator), 此时无法通过 return 返回其他数据类型

@app.post("/chat")
async def chat(req:ChatReq, api_key=Depends(check_api_key)):
    # http://127.0.0.1:8000/docs , 右上角配置 Authorize, 参考 check_api_key() 中的 valid_keys
    if req.is_stream:
        return StreamingResponse(
            call_llm_stream(req.prompt),
            media_type="text/event-stream"
        )

    return JSONResponse(
        {
            "input":req.prompt, 
            "output": await call_llm_full(req.prompt)
        }
    )
