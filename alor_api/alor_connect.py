import os
import inspect
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv, set_key
from pathlib import Path
from loguru import logger

from settings import AlorSettings


class AlorTokenManager:
    TOKEN_EXPIRATION_MINUTES = 29
    # portfolio = [
    #     "D94214",
    #     "7502NT0",
    #     "G61048"
    # ]

    def __init__(self):
        self.env_path =self._get_project_root() / '.env'
        load_dotenv(self.env_path)

    @staticmethod
    def _get_project_root() -> Path:
        current_path = Path(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
        while True:
            if (current_path / '.git').exists() or (current_path / 'pyproject.toml').exists():
                return current_path
            if current_path.parent == current_path:
                break
            current_path = current_path.parent
        return Path(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def _get_new_token(portfolio: list = None) -> None or str:
        try:
            response = requests.post(
                "https://oauth.alor.ru/refresh",
                params={
                    "token": AlorSettings().alor_refresh_token.get_secret_value(),
                    "allowedPortfolios": portfolio
                }
            )
            if response.status_code == 200:
                return response.json().get('AccessToken')
        except requests.RequestException as error:
            logger.error(f"Ошибка запроса токена: {error}")

    def _save_token_to_env(self, time: str, token: str) -> None:
        try:
            self.env_path.touch(mode=0o600, exist_ok=True)
            set_key(self.env_path, 'ALOR_ACCESS_TOKEN', token)
            set_key(self.env_path, 'TOKEN_CREATION_TIME', time)
            load_dotenv(self.env_path, override=True)
            logger.success(f"Токен обновлен и сохранен в {self.env_path}")
        except Exception as error:
            logger.error(f"Ошибка сохранения токена: {error}")

    def check_token_valid(self) -> True or None:
        count = 1
        while count >= 0:
            if AlorSettings().alor_access_token.get_secret_value():
                creation_time_str = os.getenv('TOKEN_CREATION_TIME')
                delta_time = datetime.now() - datetime.fromisoformat(creation_time_str)
                if delta_time < timedelta(minutes=self.TOKEN_EXPIRATION_MINUTES):
                    return True
                else:
                    count -= 1
                    self._save_token_to_env(datetime.now().isoformat(), self._get_new_token())
        return None


if __name__ == "__main__":
    pass
