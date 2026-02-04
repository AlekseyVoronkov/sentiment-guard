import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("AUTH_KEY")

    @property
    def SECRET_KEY_BYTES(self) -> bytes:
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY не может быть пустым!")
        return self.SECRET_KEY.encode()

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()