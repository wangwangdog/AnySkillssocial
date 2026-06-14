"""应用配置"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    APP_NAME: str = "SkillGate"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = f"sqlite:///{Path(__file__).resolve().parent.parent.parent}/data/skillgate.db"

    # JWT
    SECRET_KEY: str = "skillgate-dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 签到
    CHECKIN_DAILY_REWARD: int = 1  # 每日签到奖励次数

    # 积分
    POINTS_WITHDRAW_MIN: int = 100
    POINTS_WITHDRAW_FEE_RATE: float = 0.10

    # 存储
    UPLOAD_DIR: str = str(Path(__file__).resolve().parent.parent.parent / "uploads")

    class Config:
        env_file = ".env"


settings = Settings()
