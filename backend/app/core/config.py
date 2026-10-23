from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    database_url: str = 'postgresql+psycopg://opspilot:opspilot@db:5432/opspilot'
    secret_key: str = 'CHANGE_ME_FOR_LOCAL_DEMO_ONLY'
    demo_mode: bool = True
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-2.5-flash'
    cors_origin: str = 'http://localhost:5173'
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
settings = Settings()
