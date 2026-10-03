from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Axsikent IT"

    DATABASE_URL: str = (
        "postgresql://postgres:postgres@localhost:5432/axsikent_it"
    )

    SECRET_KEY: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5.6-luna"
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""
    BOOTSTRAP_ADMIN_PHONE: str = ""
    BOOTSTRAP_ADMIN_PASSWORD: str = ""
    BOOTSTRAP_ADMIN_NAME: str = "Axsikent Admin"
    SMS_API_URL: str = "https://send.smsxabar.uz"
    SMS_API_USERNAME: str = ""
    SMS_API_PASSWORD: str = ""
    SMS_SENDER_ID: str = "Akhsikent IT"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
