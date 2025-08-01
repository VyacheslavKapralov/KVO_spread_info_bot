import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from settings import PARAMETERS


class SettingsManager:
    def __init__(self, settings_file: str = "settings.py"):
        self.settings_file = Path(settings_file)
        self.settings = PARAMETERS.copy()

    def get_all_settings(self) -> Dict[str, Any]:
        return self.settings

    def get_setting(self, key: str) -> Optional[Any]:
        keys = key.split('.')
        value = self.settings
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return None

    def update_setting(self, key: str, value: Any) -> bool:
        keys = key.split('.')
        current = self.settings
        try:
            for k in keys[:-1]:
                current = current[k]
            current[keys[-1]] = value
            return True
        except (KeyError, TypeError):
            return False

    def save_settings(self) -> bool:
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            start_idx = None
            end_idx = None
            for i, line in enumerate(lines):
                if 'PARAMETERS = {' in line:
                    start_idx = i
                elif start_idx is not None and line.strip() == '}':
                    end_idx = i
                    break
            if start_idx is None or end_idx is None:
                raise ValueError("Не удалось найти блок PARAMETERS в файле настроек")
            new_settings = json.dumps(self.settings, indent=4, ensure_ascii=False)
            new_settings = new_settings.replace('{', '{\n').replace('}', '\n}')
            new_settings_lines = ["PARAMETERS = " + new_settings + "\n"]
            updated_lines = lines[:start_idx] + new_settings_lines + lines[end_idx + 1:]
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                f.writelines(updated_lines)
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек: {e}")
            return False


settings_manager = SettingsManager()


if __name__ == '__main__':
    logger.info('Running settings_manager.py from module utils')
