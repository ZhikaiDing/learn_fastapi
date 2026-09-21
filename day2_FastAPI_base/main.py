# 运行: cd当前目录, uvicorn main:app --reload

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

# 1. get 请求
# 1.1 路径
@app.get("/")
def hello_world():
    # http://127.0.0.1:8000/
    return {"message": "Hello world!"}

# 1.2 检验: http://127.0.0.1:8000/docs

# 1.3.1 路径参数
@app.get("/user/{uid}")
def get_user(uid:int):
    # http://127.0.0.1:8000/user/123
    return {"uid": uid}

# 1.3.2 查询参数
@app.get("/search")
def search(keyword:str, limit:int=10):
    # http://127.0.0.1:8000/search?keyword=哈基米
    return {"keyword":keyword, "limit":limit}

# 2. post 请求
class ChatRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 512
    stream: bool = False

@app.post("/chat")
def chat(req:ChatRequest):
    # 可在 http://127.0.0.1:8000/docs 调试
    return {"input":req.prompt, "output": "稍等..."}

# 3. 状态码
@app.post("/check")
def check(req:ChatRequest):
    # http://127.0.0.1:8000/doc
    return JSONResponse(
        content={"prompt": req.prompt}, 
        status_code=status.HTTP_200_OK
    )
# - 200 OK 正常
# - 201 创建成功
# - 400 请求参数错误
# - 404 找不到资源
# - 422 参数校验失败（Pydantic 校验失败默认返回）
# - 500 服务内部错误

# 4. 异常捕获
class UserRequest(BaseModel):
    uid:int = -1

@app.post("/user_v2")
def post_user(req:UserRequest):
    # http://127.0.0.1:8000/doc
    if req.uid < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="uid 错误"
        )
    return JSONResponse(
        content={"uid": req.uid},
        status_code=status.HTTP_200_OK
    )
