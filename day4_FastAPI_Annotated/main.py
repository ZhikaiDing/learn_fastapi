from fastapi import FastAPI, HTTPException, status,\
    Path, Query, Body, Header, Depends
from typing import Annotated
from pydantic import BaseModel, Field

app = FastAPI(title="Test Annotated")

#%% 1. base
# 1.1 path
@app.get("/get1/{user_name}")
def get1(user_name:str = Path()):
    return {"user": user_name}

# 1.2 query
@app.get("/search1")
def search1(keywords:str=Query(), num:int=Query(default=10)):
    return {"kewords": keywords, "num": num}

# 1.3 header
@app.get("/admin1")
def admin1(admin_key:str=Header()):
    valid_keys = ["admin-1234"]
    if admin_key in valid_keys:
        return {"state": "OK"}
    else:
        print("debug | bad admin key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad admin key")

# 1.4 body
class ChatReqBody(BaseModel):
    prompt:str
    modes:list[str] = Field(default_factory=lambda:["<data>"])

@app.post("/chat1")
def chat1(req:ChatReqBody=Body()):
    return {"prompt":req.prompt, "modes":req.modes}

#%% 2. Annotated
# 2.1 path
UsrName = Annotated[str, Path()] # 定义 类型
UsrID = Annotated[int, Path()]
@app.get("/get2/{user_name}/{uid}")
def get2(user_name:UsrName, uid:UsrID):
    return {"user": user_name, "uid":uid}

# 2.2 query
Key = Annotated[str, Query()]
Num = Annotated[int, Query()]
@app.get("/search2")
def search2(keywords:Key, num:Num=10):
    return {"kewords": keywords, "num": num}

# 2.3 header - 拆分校验逻辑
AdminKeyBase = Annotated[str, Header()]
def check_admin(admin_key:AdminKeyBase):
    valid_keys = ["admin-1234"]
    if admin_key in valid_keys:
        return admin_key
    else:
        print("debug | bad admin key")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="bad admin key")

AdminKey = Annotated[str, Depends(check_admin)]
@app.get("/admin2")
def admin2(admin_key:AdminKey):
    return {"status": "OK"}

# 2.4 body
ChatReq = Annotated[ChatReqBody, Body()]
@app.post("/chat2")
def chat2(req:ChatReq):
    return {"prompt":req.prompt, "modes":req.modes}
