from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    VERIFY_TOKEN: str = "my-secret-token"
    WHATSAPP_TOKEN: str = "placeholder-for-whatsapp-api-token"
    WHATSAPP_PHONE_NUMBER_ID: str = "placeholder-for-phone-id"
    AGENT_WORKER_URL: str = "http://agent-worker:8001"  # nombre del servicio en Docker
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()