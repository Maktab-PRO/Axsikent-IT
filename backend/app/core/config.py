from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Axsikent IT"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/axsikent_it"
    SECRET_KEY: str = "axsikent-it-secret-key-change-later"


settings = Settings()
