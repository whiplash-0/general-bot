import asyncio
from collections.abc import Awaitable, Callable, Hashable
from dataclasses import dataclass
from datetime import timedelta

from aiogram.types import Message

from general_bot.task_supervisor import TaskSupervisor
from general_bot.types import ChatId

# Function that returns a coroutine when called.
# Example: lambda: send_message(user_id)
type Job = Callable[[], Awaitable[None]]

type Messages = list[Message]
type MessageGroup = tuple[Message, ...]
type MessageGroups = list[MessageGroup]


class TaskScheduler:
    """Per-key delayed task scheduler with debounce semantics.

    Each key may have at most one pending timer. Calling `schedule()` cancels
    the previous timer and schedules `job()` to run after `delay`.

    If scheduling occurs again before the delay elapses, the previous timer is
    discarded and only the most recent job will run.

    Once the job starts executing it is shielded from cancellation and allowed
    to run to completion.
    """

    def __init__(self, task_supervisor: TaskSupervisor) -> None:
        self._tasks: dict[Hashable, asyncio.Task[None]] = {}
        self._generation: dict[Hashable, int] = {}
        self._task_supervisor = task_supervisor

    def schedule(self, job: Job, *, key: Hashable, delay: timedelta) -> None:
        self.cancel(key)
        self._generation[key] = self._generation.get(key, 0) + 1
        self._tasks[key] = self._task_supervisor.spawn(
            self._delayed(key, job, self._generation[key], delay),
        )

    def cancel(self, key: Hashable) -> None:
        if task := self._tasks.pop(key, None):
            task.cancel()

    async def _delayed(self, key: Hashable, job: Job, generation: int, delay: timedelta) -> None:
        try:
            await asyncio.sleep(delay.total_seconds())
        except asyncio.CancelledError:
            return
        if self._generation.get(key) != generation:
            return

        # Once real task started, it can't be canceled. So remove it from scheduler
        _ = self._tasks.pop(key, None)
        try:
            await asyncio.shield(job())
        except asyncio.CancelledError:
            return


class ChatMessageBuffer:
    """Chat-scoped buffer for incoming Telegram messages.

    Messages are stored by `chat_id`. `peek()` is non-destructive, while
    `flush()` and `flush_grouped()` consume buffered messages for the chat.
    Grouping is computed in `message_id` order.

    Note:
        In Telegram private chats, `chat_id` is equal to the sender's
        `user_id`. Therefore either identifier may be used as the key
        when the bot operates exclusively in personal chats.
    """

    def __init__(self) -> None:
        self._messages: dict[ChatId, Messages] = {}

    def append(self, message: Message, *, chat_id: ChatId) -> None:
        self._messages.setdefault(chat_id, []).append(message)

    def peek(self, chat_id: ChatId) -> Messages:
        return list(self._messages.get(chat_id, []))

    def flush(self, chat_id: ChatId) -> Messages:
        return self._messages.pop(chat_id, [])

    def flush_grouped(self, chat_id: ChatId) -> MessageGroups:
        """Flush and group messages by contiguous `media_group_id`."""
        return self._group(self.flush(chat_id))

    @staticmethod
    def _group(messages: Messages) -> MessageGroups:
        groups: list[Messages] = []
        ordered_messages = sorted(messages, key=lambda m: m.message_id)

        for message in ordered_messages:
            if not groups:
                groups.append([message])
                continue
            if message.media_group_id is not None and message.media_group_id == groups[-1][-1].media_group_id:
                groups[-1].append(message)
            else:
                groups.append([message])

        return [tuple(group) for group in groups]


@dataclass(frozen=True, slots=True)
class Services:
    task_scheduler: TaskScheduler
    chat_message_buffer: ChatMessageBuffer
