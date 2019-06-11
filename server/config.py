from typing import Optional

from pydantic import DSN, BaseSettings


class Config(BaseSettings):
    PROJECT_NAME = 'Debts management'
    ACCESS_TOKEN_LIFE_TIME: int = 60 * 60 * 24 * 365  # 1 year

    DATABASE_URL: DSN
    DATABASE_POOL_RECYCLE: int = 60 * 10  # 10 minutes
    DATABASE_POOL_SIZE: int = 5

    LOGGING_FORMAT: str = '%(asctime)s %(levelname)s %(name)s %(message)s'
    LOGGING_LEVEL: str = 'INFO'

    SECRET_KEY: str
    SENTRY_DSN: Optional[DSN] = None
    THREAD_POOL_SIZE: int = 10

    class Config:
        env_prefix = ''


config = Config()
