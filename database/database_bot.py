import os
import sqlite3
import json
from typing import Dict, Any, Optional, List, Tuple
from loguru import logger
from pathlib import Path


class BotDatabase:
    def __init__(self, db_path: str = 'database/database.db'):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    async def create_tables(self):
        tables = {
            'settings': """
                CREATE TABLE IF NOT EXISTS settings (
                    category TEXT,
                    key TEXT,
                    value TEXT,
                    value_type TEXT,
                    PRIMARY KEY (category, key)
                )
            """,
            'pairs': """
                CREATE TABLE IF NOT EXISTS pairs (
                    group_name TEXT,
                    pair_index INTEGER,
                    symbols TEXT,
                    coefficients TEXT,
                    PRIMARY KEY (group_name, pair_index)
                )
            """,
        }
        connect = await self.connect_database()
        cursor = connect.cursor()
        for table_name, table_sql in tables.items():
            try:
                cursor.execute(table_sql)
            except sqlite3.Error as error:
                logger.error(f"Error creating table {table_name}: {error}")
        connect.commit()
        connect.close()
        await self.initialize_default_settings()

    async def initialize_default_settings(self):
        default_technical = {
            'time_frame_minutes': ('5m', 'str'),
            'bollinger_period': (100, 'int'),
            'bollinger_deviation': (2.0, 'float'),
            'sma_period': (200, 'int'),
            'ema_period': (200, 'int'),
            'atr_period': (200, 'int'),
            'signals': (3, 'int')
        }
        default_expiration = {
            'H': '03',
            'M': '06',
            'U': '09',
            'Z': '12'
        }
        default_commands = {
            'start': 'Запустить бота',
            'main_menu': 'Вернуться в главное меню',
            'history': 'Вывести историю'
        }
        connect = await self.connect_database()
        cursor = connect.cursor()
        cursor.execute("SELECT COUNT(*) FROM settings")
        count = cursor.fetchone()[0]
        if count == 0:
            for key, (value, value_type) in default_technical.items():
                await self.save_setting('technical', key, value, value_type)
            for key, value in default_expiration.items():
                await self.save_setting('expiration_months', key, value, 'str')
            for cmd, desc in default_commands.items():
                await self.save_setting('commands', cmd, desc, 'str')
            await self.initialize_default_pairs()
        connect.close()

    async def initialize_default_pairs(self):
        default_pairs = {
            'Валюта: вечные к квартальным': [
                (('CR', 'CNYRUBF'), (1, 1)),
                (('Eu', 'EURRUBF'), (0.001, 1)),
                (('Si', 'USDRUBF'), (0.001, 1)),
            ],
            'Золото': [
                (('GL', 'GLDRUBF'), (1, 1)),
                (('GLDRUBF', 'Si', 'GD'), (31.1035, 0.001, 1)),
                (('GLDRUBF', 'USDRUBF', 'GD'), (31.1035, 1, 1)),
                (('GD', 'SV'), (1, 1))
            ],
            'Акции: вечные к квартальным': [
                (('GZ', 'GAZPF'), (0.01, 1)),
                (('MX', 'IMOEXF'), (0.1, 1)),
                (('SP', 'SBERF'), (0.01, 1)),
                (('SR', 'SBERF'), (0.01, 1)),
            ],
            'Синтетические валюты': [
                (('Eu', 'Si', 'ED'), (1, 1, 1)),
                (('EURRUBF', 'USDRUBF', 'ED'), (1, 1, 1)),
                (('Eu', 'USDRUBF', 'ED'), (0.001, 1, 1)),
                (('EURRUBF', 'Si', 'ED'), (1, 0.001, 1)),
                (('Si', 'CR', 'UC'), (0.001, 1, 1)),
                (('Si', 'CNYRUBF', 'UC'), (0.001, 1, 1)),
                (('USDRUBF', 'CR', 'UC'), (1, 1, 1)),
                (('USDRUBF', 'CNYRUBF', 'UC'), (1, 1, 1)),
            ],
            'Акции': [
                (('TATN', 'TATNP'), (1, 1)),
                (('MTLR', 'MTLRP'), (1, 1)),
                (('RTKM', 'RTKMP'), (1, 1)),
                (('SBER', 'SBERP'), (1, 1)),
                (('ROSN', 'TATN'), (1, 1)),
                (('ROSN', 'NVTK'), (1, 1)),
                (('ROSN', 'GAZP'), (1, 1)),
                (('SNGS', 'SNGSP'), (1, 1)),
                (('GMKN', 'NLMK'), (1, 1)),
                (('GMKN', 'PLZL'), (1, 1)),
                (('GMKN', 'MAGN'), (1, 1)),
                (('LKOH', 'TATN'), (1, 1)),
                (('SBER', 'VTBR'), (1, 1)),
                (('SBER', 'MOEX'), (1, 1)),
                (('CHMF', 'NLMK'), (1, 1)),
                (('CHMF', 'MAGN'), (1, 1)),
            ]
        }
        for group_name, pairs in default_pairs.items():
            for i, (symbols, coefficients) in enumerate(pairs):
                await self.save_pair(group_name, i, symbols, coefficients)

    async def connect_database(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    async def save_setting(self, category: str, key: str, value: Any, value_type: str = 'auto') -> bool:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            if value_type == 'auto':
                if isinstance(value, int):
                    value_type = 'int'
                elif isinstance(value, float):
                    value_type = 'float'
                elif isinstance(value, bool):
                    value_type = 'bool'
                elif isinstance(value, (list, tuple, dict)):
                    value_type = 'json'
                else:
                    value_type = 'str'
            if value_type == 'json':
                value_str = json.dumps(value, ensure_ascii=False)
            else:
                value_str = str(value)
            cursor.execute(
                "INSERT OR REPLACE INTO settings (category, key, value, value_type) VALUES (?, ?, ?, ?)",
                (category, key, value_str, value_type)
            )
            connect.commit()
            connect.close()
            return True
        except sqlite3.Error as error:
            logger.error(f"Error saving setting: {error}")
            return False

    async def get_setting(self, category: str, key: str) -> Optional[Any]:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute(
                "SELECT value, value_type FROM settings WHERE category = ? AND key = ?",
                (category, key)
            )
            result = cursor.fetchone()
            connect.close()

            if result:
                value_str, value_type = result
                if value_type == 'int':
                    return int(value_str)
                elif value_type == 'float':
                    return float(value_str)
                elif value_type == 'bool':
                    return value_str.lower() == 'true'
                elif value_type == 'json':
                    return json.loads(value_str)
                else:
                    return value_str
            return None
        except sqlite3.Error as error:
            logger.error(f"Error getting setting: {error}")
            return None

    async def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute("SELECT category, key, value, value_type FROM settings ORDER BY category, key")
            settings = {}
            for category, key, value_str, value_type in cursor.fetchall():
                if category not in settings:
                    settings[category] = {}
                if value_type == 'int':
                    value = int(value_str)
                elif value_type == 'float':
                    value = float(value_str)
                elif value_type == 'bool':
                    value = value_str.lower() == 'true'
                elif value_type == 'list':
                    value = json.loads(value_str)
                else:
                    value = value_str
                settings[category][key] = value
            connect.close()
            return settings
        except sqlite3.Error as error:
            logger.error(f"Error getting all settings: {error}")
            return {}

    async def delete_setting(self, category: str, key: str) -> bool:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute(
                "DELETE FROM settings WHERE category = ? AND key = ?",
                (category, key)
            )
            connect.commit()
            connect.close()
            return cursor.rowcount > 0
        except sqlite3.Error as error:
            logger.error(f"Error deleting setting: {error}")
            return False

    async def save_pair(self, group_name: str, pair_index: int, symbols: tuple, coefficients: tuple) -> bool:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            symbols_json = json.dumps(symbols)
            coefficients_json = json.dumps(coefficients)
            cursor.execute(
                "INSERT OR REPLACE INTO pairs (group_name, pair_index, symbols, coefficients) VALUES (?, ?, ?, ?)",
                (group_name, pair_index, symbols_json, coefficients_json)
            )
            connect.commit()
            connect.close()
            return True
        except sqlite3.Error as error:
            logger.error(f"Error saving pair: {error}")
            return False

    async def get_pairs(self, group_name: str = None) -> Dict[str, List[Tuple[tuple, tuple]]]:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            if group_name:
                cursor.execute(
                    "SELECT group_name, pair_index, symbols, coefficients FROM pairs WHERE group_name = ? ORDER BY pair_index",
                    (group_name,)
                )
            else:
                cursor.execute(
                    "SELECT group_name, pair_index, symbols, coefficients FROM pairs ORDER BY group_name, pair_index"
                )

            pairs = {}
            for group, index, symbols_json, coefficients_json in cursor.fetchall():
                if group not in pairs:
                    pairs[group] = []
                symbols = tuple(json.loads(symbols_json))
                coefficients = tuple(json.loads(coefficients_json))
                pairs[group].append((symbols, coefficients))
            connect.close()
            return pairs
        except sqlite3.Error as error:
            logger.error(f"Error getting pairs: {error}")
            return {}

    async def delete_pair(self, group_name: str, pair_index: int) -> bool:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute(
                "DELETE FROM pairs WHERE group_name = ? AND pair_index = ?",
                (group_name, pair_index)
            )
            connect.commit()
            connect.close()
            if cursor.rowcount > 0:
                await self.renumber_pairs(group_name)
            return True
        except sqlite3.Error as error:
            logger.error(f"Error deleting pair: {error}")
            return False

    async def renumber_pairs(self, group_name: str):
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute(
                "SELECT pair_index, symbols, coefficients FROM pairs WHERE group_name = ? ORDER BY pair_index",
                (group_name,)
            )
            pairs = cursor.fetchall()
            cursor.execute("DELETE FROM pairs WHERE group_name = ?", (group_name,))
            for new_index, (old_index, symbols, coefficients) in enumerate(pairs):
                cursor.execute(
                    "INSERT INTO pairs (group_name, pair_index, symbols, coefficients) VALUES (?, ?, ?, ?)",
                    (group_name, new_index, symbols, coefficients)
                )
            connect.commit()
            connect.close()
        except sqlite3.Error as error:
            logger.error(f"Error renumbering pairs: {error}")

    async def db_write(self, date_time: str, table_name: str, user_name: str, user_id: str, info: str = '') -> None:
        connect = await self.connect_database()
        try:
            cursor = connect.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            table_exists = cursor.fetchone()
            if not table_exists:
                cursor.execute(
                    f'''CREATE TABLE IF NOT EXISTS {table_name}
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         date_time TEXT NOT NULL,
                         user_name TEXT NOT NULL,
                         user_id TEXT NOT NULL,
                         info TEXT,
                         UNIQUE(date_time, user_id))'''
                )
                connect.commit()
                logger.info(f"Table {table_name} created")
            cursor.execute(
                f'INSERT OR IGNORE INTO {table_name} '
                '(date_time, user_name, user_id, info) '
                'VALUES (?, ?, ?, ?)',
                (date_time, user_name, user_id, info)
            )
            connect.commit()
        except sqlite3.Error as error:
            logger.error(f"Error writing to {table_name}: {error}")
        finally:
            connect.close()

    async def db_read(self, table_name: str, user_name: str) -> list:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute(f'SELECT * FROM {table_name} WHERE user_name=?', (user_name,))
            result = cursor.fetchall()
            connect.close()
            return result
        except sqlite3.Error as error:
            logger.error(f"Error reading from {table_name}: {error}")
            return []

    async def get_user(self, column: str, table_name: str) -> list:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute(f"SELECT {column} FROM {table_name}")
            result = [row[0] for row in cursor.fetchall()]
            connect.close()
            return result
        except sqlite3.Error as error:
            logger.error(f"Error getting users: {error}")
            return []

    async def get_admin(self) -> list:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            admins = [row[0] for row in cursor.execute(f"SELECT user_name FROM administrators").fetchall()]
            connect.close()
            return admins
        except sqlite3.Error as error:
            logger.error(f"Error getting admins: {error}")
            return []

    async def get_bot_commands(self) -> Dict[str, str]:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute("SELECT key, value FROM settings WHERE category = 'commands' AND key != 'commands'")
            commands = {}
            for key, value in cursor.fetchall():
                commands[key] = value
            connect.close()
            if not commands:
                return {
                    'start': 'Запустить бота',
                    'main_menu': 'Вернуться в главное меню',
                    'history': 'Вывести историю'
                }
            return commands
        except sqlite3.Error as error:
            logger.error(f"Error getting bot commands: {error}")
            return {
                'start': 'Запустить бота',
                'main_menu': 'Вернуться в главное меню',
                'history': 'Вывести историю'
            }

    async def get_expiration_months(self) -> Dict[str, str]:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute("SELECT key, value FROM settings WHERE category = 'expiration'")
            expiration_months = {}
            for key, value in cursor.fetchall():
                expiration_months[key] = value
            connect.close()
            if not expiration_months:
                return {
                    'H': '03',
                    'M': '06',
                    'U': '09',
                    'Z': '12'
                }
            return expiration_months
        except sqlite3.Error as error:
            logger.error(f"Error getting expiration months: {error}")
            return {
                'H': '03',
                'M': '06',
                'U': '09',
                'Z': '12'
            }

    async def get_pairs_formatted(self) -> Dict[str, List[Tuple[tuple, tuple]]]:
        try:
            connect = await self.connect_database()
            cursor = connect.cursor()
            cursor.execute("SELECT group_name, symbols, coefficients FROM pairs ORDER BY group_name, pair_index")
            pairs = {}
            for group_name, symbols_json, coefficients_json in cursor.fetchall():
                if group_name not in pairs:
                    pairs[group_name] = []
                symbols = tuple(json.loads(symbols_json))
                coefficients = tuple(json.loads(coefficients_json))
                pairs[group_name].append((symbols, coefficients))
            connect.close()
            return pairs
        except sqlite3.Error as error:
            logger.error(f"Error getting formatted pairs: {error}")
            return {}


db = BotDatabase()


if __name__ == '__main__':
    logger.info('Running database.py from module database')
