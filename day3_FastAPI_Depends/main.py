from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Annotated, Generator

app = FastAPI()

class TestRequest(BaseModel):
    uid:int = -1
    input:str = ""
    temperature:float = 0.7

def check_req(req:TestRequest):
    if req.uid < 0:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, 
            detail = "bad uid"
        )

    return req

# 1. Dpends 基础
@app.post("/test1")
def test1(req:TestRequest = Depends(check_req)):
    # http://127.0.0.1:8000/docs
    
    return JSONResponse(
        content={
            "user_id": req.uid,
            "input": req.input,
            "answer": "请稍等..."
        }, 
        status_code=status.HTTP_200_OK
    )

# 2. Dpends 嵌套
class FakeDB:
    def __init__(self):
        print("Data base is initialized.")
        self.datas = ["a", "b", "c"]
    
    def search_by_id(self, i:int=0):
        n = len(self.datas)
        if i >= n:
            raise IndexError(f"i={i} out of range") # 假设数据库抛普通异常，在依赖层翻译。
        return self.datas[i]
    
    def close(self):
        print("Data base is closed.")

class SearchReq(BaseModel):
    data_id: int = 0
    modes: list[str] = Field(default_factory=lambda: ["<data>"])
    # 如果直接写 modes = ["<data>"], 可能会有共享默认数据的风险
    #   假设真的共享了默认数据，而某个函数有“修改”了这个数据，则会污染后面所用使用默认数据的请求
    # 当然，实际上 Pydantic v2 在实例化时会复制可变的默认值，比较安全
    #   不过还是推荐用 Field 的 default_factory, 显式表示：在每次使用时生成新的默认值

def get_db_session() -> Generator[FakeDB, None, None]:
    db_session = FakeDB()
    try:
        yield db_session # 把 db 交给下一个依赖/接口函数, 用于生命周期管理
    finally:
        db_session.close() # 原则：谁创建，谁关闭, 即只需要在这里写

def get_db_data(
        payload: SearchReq, 
        db: FakeDB = Depends(get_db_session)
) -> Generator[str, None, None]:
    # 注意这里的入参是 payload, 也就是 请求体数据
    # 虽然本函数只用到了 data_id, 但是也需要传入 请求体数据
    try:
        return db.search_by_id(payload.data_id)
        # 这里用 return 即可, 因为不需要对 db 和 search 的结果做资源管理
    except IndexError:
        raise HTTPException(404, f"data_id={payload.data_id} not found") # 404 表示找不到资源

def deal_db_data(
        payload: SearchReq, # 同一个 body，FastAPI 会分别解析，没问题
        data: str = Depends(get_db_data),
):
    templates = []
    for mode in payload.modes:
        if "data" not in mode:
            raise HTTPException(422, f"bad mode: {mode}")
        templates.append(mode.replace("data", data))
    return {"data": data, "templates": templates}

@app.post("/test2")
def test2(req=Depends(deal_db_data)):
    return JSONResponse(content=req)

# 注：
# 一个函数的入参可以有多个 Depends
# 多个函数可以 Depends 同一个函数
# 生命周期: 不是 "最后一个依赖它的函数刚用完就释放"，而是 "整个请求处理完、响应发送给客户端之后" 才释放。
