from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER : str
    DB_PASSWORD : str
    DB_HOST : str
    DB_PORT : int
    DB_NAME : str

    APP_NAME : str
    
    DEBUG: bool = False
    
    SESSION_EXPIRE_MINUTES : int = 60
    
    COOKIE_SECURE : bool = True
    
    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    SMTP_FROM_EMAIL: str
    
    PASSWORD_RESET_EXPIRE_MINUTES : int = 15
    EMAIL_VERIFICATION_EXPIRE_MINUTES : int = 30
    FRONTEND_URL : str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()