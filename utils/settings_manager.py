import json
from typing import Dict, Any, Optional

from loguru import logger

from database.database_bot import BotDatabase, db


class SettingsManager:
    def __init__(self, database: BotDatabase):
        self.db = database

    async def get_all_settings(self) -> Dict[str, Any]:
        settings = await self.db.get_all_settings()
        result = {
            'expiration_months': settings.get('expiration'),
            'time_frame_minutes': settings.get('technical').get('time_frame_minutes'),
            'bollinger_period': settings.get('technical').get('bollinger_period'),
            'bollinger_deviation': settings.get('technical').get('bollinger_deviation'),
            'sma_period': settings.get('technical').get('sma_period'),
            'ema_period': settings.get('technical').get('ema_period'),
            'atr_period': settings.get('technical').get('atr_period'),
            'signals': settings.get('technical').get('signals'),
            'pairs': await self.db.get_pairs(),
            'commands': settings.get('commands')
        }
        return result

    async def get_setting(self, key: str) -> Optional[Any]:
        keys = key.split('.')
        if len(keys) == 1:
            return await self.db.get_setting('technical', keys[0])
        elif len(keys) == 2:
            return await self.db.get_setting(keys[0], keys[1])
        return None

    async def update_setting(self, key: str, value: Any) -> bool:
        keys = key.split('.')
        if len(keys) == 1:
            category = 'technical'
            setting_key = keys[0]
        elif len(keys) == 2:
            category, setting_key = keys
        else:
            return False
        if isinstance(value, int):
            value_type = 'int'
        elif isinstance(value, float):
            value_type = 'float'
        elif isinstance(value, bool):
            value_type = 'bool'
        elif isinstance(value, (list, tuple)):
            value_type = 'list'
            value = json.dumps(value)
        else:
            value_type = 'str'
        return await self.db.save_setting(category, setting_key, value, value_type)

    async def delete_setting(self, key: str) -> bool:
        keys = key.split('.')
        if len(keys) == 1:
            category = 'technical'
            setting_key = keys[0]
        elif len(keys) == 2:
            category, setting_key = keys
        else:
            return False
        return await self.db.delete_setting(category, setting_key)


settings_manager = SettingsManager(db)

if __name__ == '__main__':
    logger.info('Running settings_manager.py from module utils')
