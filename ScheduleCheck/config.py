from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_username: str | None = None
    mongodb_password: str | None = None
    mongodb_database: str = "notifications"
    mongodb_ssl: bool = False
    mongodb_retrywrites: bool = True
    base_url: str = "base_url"

settings = Settings()
