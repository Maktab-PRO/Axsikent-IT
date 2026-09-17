from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Axsikent IT"

    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/axsikent_it"
    )

    SECRET_KEY: str = "axsikent-it-secret-key-change-later"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
