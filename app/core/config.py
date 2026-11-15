from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]   # 项目根目录


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Todo API"
    secret_key: str                                   # 没有默认值 = 缺了就直接启动失败
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = f"sqlite:///{(BASE_DIR / 'todo.db').as_posix()}"
    log_level: str = "INFO"

settings = Settings()  # type: ignore[call-arg]  # 值由 .env 在运行时注入