from collections.abc import Awaitable
from typing import Any, Callable

from aiogram.types import TelegramObject

type Data = dict[str, Any]
type Handler = Callable[[TelegramObject, Data], Awaitable[Any]]

type ChatId = int
type UserId = int
