import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


class Settings:
    ALGORITHM = os.getenv("ALGORITHM")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DATABASE_URL: str = "sqlite:///./videoman.db"


settings = Settings()
