from typing import Optional

from pydantic import DSN, BaseSettings


class Config(BaseSettings):
    PROJECT_NAME = 'Debts management'
    DATABASE: DSN
    SECRET_KEY: str
    ACCESS_TOKEN_LIFE_TIME: int = 60 * 60 * 24 * 365  # 1 year
    ENVIRONMENT: Optional[str] = None
    SENTRY_DSN: Optional[DSN] = None
    LOGGING_LEVEL: str = 'INFO'
    LOGGING_FORMAT: str = '%(asctime)s %(levelname)s %(name)s %(message)s'

    class Config:
        env_prefix = ''


config = Config()
