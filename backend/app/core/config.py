from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Axsikent IT"

    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/axsikent_it"
    )

    SECRET_KEY: str = "axsikent-it-secret-key-change-later"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5.6-luna"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
