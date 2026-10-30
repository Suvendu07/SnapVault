from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER : str
    DB_PASSWORD : str
    DB_HOST : str
    DB_PORT : int
    DB_NAME : str

    APP_NAME : str
    
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()