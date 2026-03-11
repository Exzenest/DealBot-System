from typing import Callable, Awaitable, Dict, Any
from aiogram import BaseMiddleware
from src.database.base import session_maker


class DataBaseSession(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[[Dict[str, Any]], Awaitable[Any]],
            event: Any,
            data: Dict[str, Any]
    ) -> Any:

        async with session_maker() as session:
            data["session"] = session
            return await handler(event, data)
