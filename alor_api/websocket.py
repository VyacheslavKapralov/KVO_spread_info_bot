import asyncio
import json
import queue
from datetime import datetime

import pandas as pd
from websockets import connect, ConnectionClosed, ConnectionClosedOK
from loguru import logger

from alor_api.alor_connect import AlorTokenManager
from alor_api.http_get_data import get_info_symbol
from settings import AlorSettings


class AlorWebsocket:
    def __init__(self, data_handler):
        self.data_handler = data_handler
        self.ws_url = "wss://api.alor.ru/ws"
        self.guid = []
        self.token_manager = AlorTokenManager()
        self.active_connections = {}
        self._subscriptions = {}
        self._running = False
        self._reconnect_tasks = {}
        self._listen_tasks = {}

    async def get_data_for_gui(self):
        with open('test_data_frame/data_frame.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for symbol, df_data in data.items():
            data_frame = pd.DataFrame.from_records(df_data['data'])
            data_frame = data_frame.drop(columns=['Last_volume', 'Interval'], errors='ignore')
            data_frame['Time'] = pd.to_datetime(data_frame['Time'], format='%Y-%m-%d %H:%M:%S.%f')
            data_frame[['Price', 'Volume', 'Timestamp']] = data_frame[['Price', 'Volume', 'Timestamp']].apply(pd.to_numeric)
            for _, row in data_frame.iterrows():
                self.data_handler.trades_queue.put_nowait({
                    'symbol': symbol,
                    'trade': row.tolist()
                })

    async def start(self):
        if self._running:
            return
        self._running = True
        logger.info("Запуск AlorWebsocket...")
        for symbol, subscribe_message in self._subscriptions.items():
            await self._connect_websocket(subscribe_message)

    async def stop(self):
        if not self._running:
            return
        self._running = False
        logger.info("Остановка AlorWebsocket...")
        for task in self._reconnect_tasks.values():
            task.cancel()
        self._reconnect_tasks.clear()
        await self.disconnect_all_websockets()
        for task in self._listen_tasks.values():
            task.cancel()
        self._listen_tasks.clear()

    async def orderbook(self, symbol: str = "SBER", depth=200):
        if not self._running:
            await self.start()
        subscribe_message = await self._prepare_subscription(
            "OrderBookGetAndSubscribe",
            symbol,
            depth=depth
        )
        self._subscriptions[symbol] = subscribe_message
        if self._running:
            await self._connect_websocket(subscribe_message)

    async def trades(self, symbol: str = "SBER", depth=1):
        if not self._running:
            await self.start()
        info_symbol = await get_info_symbol(symbol)
        subscribe_message = await self._prepare_subscription(
            "AllTradesGetAndSubscribe",
            symbol,
            depth=depth,
            instrumentGroup=info_symbol.get('board')
        )
        self._subscriptions[symbol] = subscribe_message
        if self._running:
            await self._connect_websocket(subscribe_message)

    async def candles(self, from_time: int, symbol: str = 'SBER', time_frame: str = '3600'):
        if not self._running:
            await self.start()
        info_symbol = await get_info_symbol(symbol)
        subscribe_message = await self._prepare_subscription(
            "BarsGetAndSubscribe",
            symbol,
            instrumentGroup=info_symbol.get('board'),
            tf=time_frame,
            skipHistory=False,
            splitAdjust=True
        )
        self._subscriptions[symbol] = subscribe_message
        self._subscriptions[symbol].update('from', from_time)
        if self._running:
            await self._connect_websocket(subscribe_message)

    async def _prepare_subscription(self, opcode, symbol, **kwargs):
        if not self.token_manager.check_token_valid():
            raise Exception("Просроченный или некорректный Access Токен")
        message = {
            "opcode": opcode,
            "code": symbol,
            "exchange": "MOEX",
            "format": "Simple",
            "guid": symbol,
            "token": AlorSettings().alor_access_token.get_secret_value()
        }
        message.update(kwargs)
        return message

    async def _connect_websocket(self, subscribe_message: dict):
        symbol = subscribe_message['code']
        if symbol in self.active_connections:
            logger.info(f"Уже есть активное соединение для {symbol}")
            return
        self.guid.append(symbol)
        try:
            websocket = await connect(self.ws_url)
            self.active_connections[symbol] = websocket
            await self._safe_send(websocket, subscribe_message)
            self._listen_tasks[symbol] = asyncio.create_task(self._listen_websocket(websocket, symbol))
            logger.success(f"Успешное подключение к {self.ws_url}: {subscribe_message['opcode']}, {symbol}")
        except Exception as error:
            logger.error(f"Ошибка подключения для {symbol}: {error} строка - {error.__traceback__.tb_lineno}")
            await self._schedule_reconnect(symbol)

    async def _listen_websocket(self, websocket, symbol: str):
        try:
            while self._running and symbol in self.active_connections:
                try:
                    message = await websocket.recv()
                    await self._process_message(message, symbol)
                except (ConnectionClosed, ConnectionClosedOK) as error:
                    if self._running:
                        logger.error(f"Соединение для {symbol} разорвано: code={error.code}, reason={error.reason}")
                        await self._schedule_reconnect(symbol)
                    break
                except Exception as error:
                    logger.error(f"Ошибка при обработке сообщения для {symbol}: "
                                 f"{error} строка - {error.__traceback__.tb_lineno}")
                    if self._running:
                        await self._schedule_reconnect(symbol)
                    break
        finally:
            if symbol in self.active_connections:
                self.active_connections.pop(symbol)
            await self._close_websocket(websocket)

    async def _schedule_reconnect(self, symbol: str):
        if symbol in self._reconnect_tasks or symbol not in self._subscriptions:
            return

        async def reconnect_task():
            await asyncio.sleep(1)
            try:
                if self._running and symbol in self._subscriptions:
                    logger.info(f"Пытаемся переподключиться для {symbol}")
                    await self._connect_websocket(self._subscriptions[symbol])
            except Exception as error:
                logger.error(f"Ошибка переподключения для {symbol}: {error} строка - {error.__traceback__.tb_lineno}")
            finally:
                self._reconnect_tasks.pop(symbol, None)

        self._reconnect_tasks[symbol] = asyncio.create_task(reconnect_task())

    async def _process_message(self, message: str, symbol: str):
        try:
            websocket_data = json.loads(message)
            if not websocket_data.get('data'):
                return
            subscription = self._subscriptions.get(symbol, {})
            opcode = subscription.get('opcode')
            if opcode == "OrderBookGetAndSubscribe":
                orderbook_data = {
                    'type': 'orderbook',
                    'symbol': websocket_data['data'].get('symbol'),
                    'orders': {
                        'bids': websocket_data['data'].get('bids', []),
                        'asks': websocket_data['data'].get('asks', []),
                        'timestamp': websocket_data.get("timestamp")
                    }
                }
                try:
                    self.data_handler.orderbook_queue.put_nowait(orderbook_data)
                except queue.Full:
                    self.data_handler.orderbook_queue.put_nowait(orderbook_data)
                    logger.warning(f"Очередь стакана переполнена")
            elif opcode == "AllTradesGetAndSubscribe":
                timestamp_hit = websocket_data['data'].get('timestamp')
                time_hit = datetime.fromtimestamp(timestamp_hit / 1000)
                trades_data = {
                    'type': 'trades',
                    'symbol': websocket_data['data'].get('symbol'),
                    'trade': (
                        time_hit,
                        websocket_data['data'].get('price'),
                        websocket_data['data'].get('side'),
                        websocket_data['data'].get('qty'),
                        timestamp_hit
                    )
                }
                try:
                    self.data_handler.trades_queue.put_nowait(trades_data)
                    # logger.info(f"\nДобавлен в очередь \n{trades_data}. "
                    #             f"Длина очереди {self.data_handler.trades_queue.qsize()}")
                except queue.Full:
                    self.data_handler.trades_queue.put_nowait(trades_data)
                    logger.warning(f"Очередь сделок переполнена")
            elif opcode == "BarsGetAndSubscribe":
                candles_data = {
                    'type': 'candles',
                    'symbol': websocket_data['data'].get('symbol'),
                    'candle': {
                        'timestamp': websocket_data['data'].get('time'),
                        'open': websocket_data['data'].get('open'),
                        'high': websocket_data['data'].get('high'),
                        'low': websocket_data['data'].get('low'),
                        'close': websocket_data['data'].get('close'),
                        'volume': websocket_data['data'].get('volume')
                    }
                }
                try:
                    self.data_handler.candles_queue.put_nowait(candles_data)
                except queue.Full:
                    self.data_handler.candles_queue.put_nowait(candles_data)
                    logger.warning(f"Очередь свечей переполнена")
        except Exception as error:
            logger.error(f"Ошибка обработки сообщения для {symbol}: {error} строка - {error.__traceback__.tb_lineno}")

    @staticmethod
    async def _safe_send(websocket, message: dict):
        try:
            await websocket.send(json.dumps(message))
        except Exception as error:
            logger.error(f"Ошибка при отправке сообщения ({message}): {error} строка - {error.__traceback__.tb_lineno}")
            raise

    async def disconnect_all_websockets(self):
        if not self.active_connections:
            logger.info("Нет активных соединений для отключения")
            return
        logger.info(f"Начинаем отключение {len(self.active_connections)} соединений...")
        for task in self._reconnect_tasks.values():
            task.cancel()
        self._reconnect_tasks.clear()
        tasks = []
        for symbol, websocket in list(self.active_connections.items()):
            tasks.append(self._disconnect_single(symbol, websocket))
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.success("Все соединения отключены")

    async def _disconnect_single(self, symbol: str, websocket):
        try:
            unsubscribe_message = {
                "opcode": "unsubscribe",
                "guid": symbol,
                "token": AlorSettings().alor_access_token.get_secret_value()
            }
            await self._safe_send(websocket, unsubscribe_message)
            if symbol in self.active_connections:
                self.active_connections.pop(symbol)
            if symbol in self.guid:
                self.guid.remove(symbol)
            logger.success(f"Соединение для {symbol} успешно закрыто")
        except ConnectionClosed:
            logger.info(f"Соединение для {symbol} уже закрыто сервером")
        except Exception as error:
            logger.error(f"Ошибка при отключении {symbol}: {error} строка - {error.__traceback__.tb_lineno}")
        finally:
            await self._close_websocket(websocket)

    @staticmethod
    async def _close_websocket(websocket):
        try:
            if websocket and not websocket.state.CLOSED:
                await websocket.close()
        except Exception as error:
            logger.error(f"Ошибка при закрытии соединения: {error} строка - {error.__traceback__.tb_lineno}")


if __name__ == "__main__":
    pass
