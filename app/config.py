from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    database_url : str 
    mwapi_api_key : str 
    embedding_dim : int = 1536

    model_config = SettingsConfigDict (
        env_file = ".env",
        extra = "ignore"
    )

settings = Settings()