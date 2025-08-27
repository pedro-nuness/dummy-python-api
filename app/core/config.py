from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    EXTERNAL_API_BASE_URL: str
    LOG_LEVEL: str = "INFO"
    
    CIRCUIT_BREAKER_FAIL_MAX: int = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 30 # in seconds

settings = Settings()