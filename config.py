import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DATABASE_URL: str = _require("DATABASE_URL")
SECRET_KEY: str = _require("SECRET_KEY")
JWT_SECRET: str = _require("JWT_SECRET")
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRY_SECONDS: int = 3600