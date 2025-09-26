import os
import ast
from typing import List
from functools import lru_cache

from pydantic_settings import (
    BaseSettings, SettingsConfigDict)
from pydantic import Field, field_validator, validator

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or .env file.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # APP settings
    APP_NAME: str = os.environ['APP_NAME']
    DEBUG: bool = os.environ['DEBUG']

    # JWT Settings
    SECRET_KEY: str = os.environ['SECRET_KEY']
    ALGORITHM: str = os.environ['ALGORITHM']
    LOGIN_ACCESS_TOKEN_EXPIRY: int = os.environ['LOGIN_ACCESS_TOKEN_EXPIRY'] # Expiry 24 hours
    FORGOT_PASSWORD_EXPIRY: int = os.environ['FORGOT_PASSWORD_EXPIRY']
    INVITATION_TOKEN_EXPIRY: int = os.environ['INVITATION_TOKEN_EXPIRY']
    EMAIL_CONFIRMATION_TOKEN_TTL: int = os.environ['EMAIL_CONFIRMATION_TOKEN_TTL']

    # Database settings
    POSTGRES_USER: str = os.environ['POSTGRES_USER']
    POSTGRES_PASSWORD: str = os.environ['POSTGRES_PASSWORD']
    POSTGRES_DB: str = os.environ['POSTGRES_DB']
    POSTGRES_HOST: str = os.environ['POSTGRES_HOST']
    POSTGRES_PORT: int = os.environ['POSTGRES_PORT']
    DATABASE_URL: str = os.environ['DATABASE_URL'] # .replace("postgresql://", "postgresql+asyncpg://")
    DATABASE_POOL_SIZE: int = os.environ['DATABASE_POOL_SIZE']
    DATABASE_MAX_OVERFLOW: int = os.environ['DATABASE_MAX_OVERFLOW']
    DATABASE_POOL_RECYCLE_IN_SECONDS: int = os.environ['DATABASE_POOL_RECYCLE_IN_SECONDS']
    DATABASE_POOL_TIMEOUT_IN_SECONDS: int = os.environ['DATABASE_POOL_TIMEOUT_IN_SECONDS']
    DATABASE_CONNECT_TIMEOUT: int = os.environ['DATABASE_CONNECT_TIMEOUT']

    # Redis settings
    REDIS_HOST: str = os.environ['REDIS_HOST']
    REDIS_PORT: int = os.environ['REDIS_PORT']
    REDIS_DB: int = os.environ['REDIS_DB']
    REDIS_PASSWORD: str =  os.environ['REDIS_PASSWORD']
    REDIS_URL: str = os.environ['REDIS_URL']

    # SendGrid Configuration
    SENDGRID_FROM_EMAIL: str = os.environ['SENDGRID_FROM_EMAIL']
    SENDGRID_API_KEY: str = os.environ['SENDGRID_API_KEY']

    # Brevo Configuration
    BREVO_API_KEY: str = os.environ['BREVO_API_KEY']
    BREVO_SENDER_EMAIL: str = os.environ['BREVO_SENDER_EMAIL']
    
    # Front-end
    FRONT_END_BASE_URL: str = os.environ['FRONT_END_BASE_URL']
    FRONT_END_REGISTRATION_URL: str = os.environ['FRONT_END_REGISTRATION_URL']
    FRONT_END_PASSWORD_RESET_URL: str = os.environ['FRONT_END_PASSWORD_RESET_URL']

    # OpenAI Settings
    OPEN_AI_API_KEY: str = os.environ['OPEN_AI_API_KEY'] 
    OPEN_AI_MODEL: str = os.environ['OPEN_AI_MODEL']
    OPEN_AI_PROMPT_BEHAVIOUR: str = os.environ['OPEN_AI_PROMPT_BEHAVIOUR']
    OPEN_AI_PROMPT_MAX_TOKEN: int = os.environ['OPEN_AI_PROMPT_MAX_TOKEN']

    # Azure
    AZURE_ENDPOINT: str = os.environ['AZURE_ENDPOINT']
    AZURE_SUBSCRIPTION_KEY: str = os.environ['AZURE_SUBSCRIPTION_KEY']
    AZURE_API_VERSION: str = os.environ['AZURE_API_VERSION']
    AZURE_MAX_COMPLETION_TOKEN_LIMIT: str = os.environ['AZURE_MAX_COMPLETION_TOKEN_LIMIT']

    # Sendgrid
    SENDGRID_API_KEY: str = os.environ['SENDGRID_API_KEY']
    SENDGRID_FROM_EMAIL: str = os.environ['SENDGRID_FROM_EMAIL']

    # AWS 
    AWS_ACCESS_KEY_ID: str = os.environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_ACCESS_KEY: str = os.environ['AWS_SECRET_ACCESS_KEY']
    AWS_REGION: str = os.environ['AWS_REGION']
    S3_BUCKET_NAME: str = os.environ['S3_BUCKET_NAME']

    # System Timezone
    TIMEZONE: str = os.environ['TIMEZONE'] 
    # Alert to Developers
    DEVELOPERS_EMAILS: list[str] | str = "" 

    @field_validator("DEVELOPERS_EMAILS", mode="before")
    def split_emails(cls, v):
        print("inti*****")
        if isinstance(v, str):
            return [email.strip() for email in v.split(",") if email.strip()]
        return v
# @lru_cache()
# def get_settings():
#     """
#     Memoized function to get application settings.
#     Ensures settings are loaded only once.
#     """
#     return Settings()

settings = Settings()