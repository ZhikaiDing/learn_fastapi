from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT:str

    DATABASE_URL:str

    DEFAULT_LLM_MODEL:str
    DEFAULT_LLM_API_KEY:str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf8")

settings = Settings()
# print(settings.DATABASE_URL)
