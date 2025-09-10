import asyncio
from datetime import datetime
from typing import Dict

from loguru import logger


class SpreadMonitor:
    def __init__(self):
        self.active_monitors: Dict[int, Dict[str, dict]] = {}
        self.lock = asyncio.Lock()

    async def add_monitor(self, user_id: int, monitor_id: str, task: asyncio.Task, data: dict):
        async with self.lock:
            if user_id not in self.active_monitors:
                self.active_monitors[user_id] = {}
            self.active_monitors[user_id][monitor_id] = {
                'task': task,
                'data': data,
                'active': True
            }

    async def remove_monitor(self, user_id: int, monitor_id: str) -> bool:
        async with self.lock:
            if user_id in self.active_monitors and monitor_id in self.active_monitors[user_id]:
                self.active_monitors[user_id][monitor_id]['task'].cancel()
                del self.active_monitors[user_id][monitor_id]
                return True
        return False

    async def remove_all_user_monitors(self, user_id: int) -> int:
        async with self.lock:
            if user_id in self.active_monitors:
                count = len(self.active_monitors[user_id])
                for monitor_id in list(self.active_monitors[user_id].keys()):
                    self.active_monitors[user_id][monitor_id]['task'].cancel()
                del self.active_monitors[user_id]
                return count
        return 0

    async def get_user_monitors(self, user_id: int) -> Dict[str, dict]:
        async with self.lock:
            return self.active_monitors.get(user_id, {}).copy()

    async def is_monitor_active(self, user_id: int, monitor_id: str) -> bool:
        async with self.lock:
            if user_id in self.active_monitors and monitor_id in self.active_monitors[user_id]:
                return self.active_monitors[user_id][monitor_id]['active']
        return False

    async def pause_monitor(self, user_id: int, monitor_id: str) -> bool:
        async with self.lock:
            if user_id in self.active_monitors and monitor_id in self.active_monitors[user_id]:
                self.active_monitors[user_id][monitor_id]['active'] = False
                return True
        return False

    async def resume_monitor(self, user_id: int, monitor_id: str) -> bool:
        async with self.lock:
            if user_id in self.active_monitors and monitor_id in self.active_monitors[user_id]:
                self.active_monitors[user_id][monitor_id]['active'] = True
                return True
        return False


def generate_monitor_id(tickers: list, strategy: str) -> str:
    tickers_str = "_".join(tickers)
    timestamp = int(datetime.now().timestamp())
    return f"{strategy}_{tickers_str}_{timestamp}"


if __name__ == '__main__':
    logger.info('Running spread_monitor.py from module telegram_api/essence')
