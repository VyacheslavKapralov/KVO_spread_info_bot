import os
import sqlite3

from loguru import logger


class BotDatabase:

    @logger.catch()
    async def create_file_database(self):
        tables = (
            'allowed_ids',
            'incoming_ids',
            'bot_lines_signals',
            'bot_bb_signals',
            'administrators',
        )
        db_path = 'database/database.db'
        if not os.path.exists(db_path):
            for table_name in tables:
                await self.create_database(table_name)

    @logger.catch()
    async def create_database(self, table_name: str) -> None:
        connect = await connect_database()
        cursor = connect.cursor()
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                            date_time TEXT,
                            user_name TEXT,
                            user_id INTEGER PRIMARY KEY,
                            info TEXT
                            )"""
                       )
        connect.commit()
        cursor.close()
        connect.close()

    # @logger.catch()
    # async def create_ticker_database(self, table_name: str) -> None:
    #     connect = await connect_database()
    #     cursor = connect.cursor()
    #     cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
    #                         ticker TEXT PRIMARY KEY,
    #                         expiration_date TEXT
    #                         )"""
    #                    )
    #     connect.commit()
    #     cursor.close()
    #     connect.close()

    @logger.catch()
    async def db_write(self, date_time: str, table_name: str, user_name: str, user_id: str, info: str = '') -> None:
        while True:
            try:
                connect = await connect_database()
                cursor = connect.cursor()
                cursor.execute(
                    f'INSERT OR IGNORE INTO {table_name} '
                    '('
                    'date_time,'
                    'user_name,'
                    'user_id,'
                    'info'
                    ')'
                    'VALUES (?, ?, ?, ?)',
                    (
                        date_time,
                        user_name,
                        user_id,
                        info
                    )
                )
                connect.commit()
                connect.close()
                break
            except sqlite3.OperationalError as error:
                logger.error(f"Error: {error}")
                await self.create_database(table_name)

    # @logger.catch()
    # async def db_write_ticker_info(self, table_name: str, expiration_date: str, ticker: str) -> None:
    #     connect = await connect_database()
    #     cursor = connect.cursor()
    #     cursor.execute(
    #         f'UPDATE {table_name} '
    #         'SET expiration_date = ? '
    #         'WHERE ticker = ?',
    #         (
    #             expiration_date,
    #             ticker
    #         )
    #     )
    #     if cursor.rowcount == 0:
    #         cursor.execute(
    #             f'INSERT INTO {table_name} '
    #             '(ticker, expiration_date) '
    #             'VALUES (?, ?)',
    #             (
    #                 ticker,
    #                 expiration_date
    #             )
    #         )
    #     connect.commit()
    #     connect.close()

    @logger.catch()
    async def db_read(self, table_name: str, user_name: str) -> list:
        connect = await connect_database()
        cursor = connect.cursor()
        try:
            info = [row for row in cursor.execute(f'SELECT * FROM {table_name} WHERE user_name=?',
                                                  (user_name,)).fetchall()]
            return info
        except sqlite3.OperationalError as error:
            logger.error(f"Error: {error}.")
        finally:
            connect.close()

    # @logger.catch()
    # async def db_read_ticker_info(self, table_name: str, ticker: str) -> list or None:
    #     connect = await connect_database()
    #     cursor = connect.cursor()
    #     try:
    #
    #         info = cursor.execute(f'SELECT * FROM {table_name} WHERE ticker=?', (ticker,)).fetchall()
    #         return info[0]
    #     except (IndexError, sqlite3.OperationalError) as error:
    #         logger.error(f"Error: {error}.")
    #         return
    #     finally:
    #         connect.close()

    @logger.catch()
    async def get_user(self, column: str, table_name: str) -> list:
        connect = await connect_database()
        cursor = connect.cursor()
        try:
            user = [row[0] for row in cursor.execute(f"SELECT {column} FROM {table_name}").fetchall()]
            return user
        except sqlite3.OperationalError as error:
            logger.error(f"Error: {error}.")
        finally:
            connect.close()

    @logger.catch()
    async def get_admin(self) -> list:
        connect = await connect_database()
        cursor = connect.cursor()
        try:
            admins = [row[0] for row in cursor.execute(f"SELECT user_name FROM administrators").fetchall()]
            return admins
        except sqlite3.OperationalError as error:
            logger.error(f"Error: {error}.")
        finally:
            connect.close()

    async def deleting_user_db(self, table_name: str, user_id: int):
        connect = await connect_database()
        cursor = connect.cursor()
        try:
            info = [row for row in cursor.execute(f'SELECT * FROM {table_name} WHERE user_id=?',
                                                  (user_id,)).fetchall()]
            return info
        except sqlite3.OperationalError as error:
            logger.error(f"Error: {error}.")
        finally:
            connect.close()


@logger.catch()
async def connect_database():
    return sqlite3.connect('database/database.db', check_same_thread=False)


if __name__ == '__main__':
    logger.info('Running database.py from module database')
