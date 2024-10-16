import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn

# from sqlalchemy.engine import URL
import os
import sys
from dotenv import load_dotenv

home_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(home_dir)

load_dotenv(dotenv_path=f'{home_dir.replace(os.sep+"app", "")}{os.sep}{".env"}')
load_dotenv()


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings:
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    API_KEY = os.getenv("OPENAI_API_KEY")

    assert (
        API_KEY is not None
    ), "Please add the OpenAI api key variable 'OPENAI_API_KEY' to the .env file with a valid api key"

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = parse_cors(
        v="http://finbot.localhost, https://finbot.localhost, finbot.localhost, http://localhost, http://localhost:8282, https://localhost, https://localhost:8282"
    )

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", None)


settings = Settings()
