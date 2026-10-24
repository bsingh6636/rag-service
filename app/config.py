from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    database_url : str 
    mwapi_api_key : str 
    embedding_dim : int = 1536
    mwapi_url : str =  "https://api.mwapi.dev/v1"
    chat_model: str = "claude-haiku-4-5-20251001"

    model_config = SettingsConfigDict (
        env_file = ".env",
        extra = "ignore"
    )

settings = Settings()