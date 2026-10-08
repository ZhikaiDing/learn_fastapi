from fastapi import FastAPI
from api.v1 import api_router

app = FastAPI(title="AI对话应用后端", version="0.1.0")
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"msg": "AI Chat Backend Running"}
