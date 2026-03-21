from collections.abc import Awaitable, Callable

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, ErrorEvent, KeyboardButton, Message, ReplyKeyboardMarkup
from loguru import logger

from general_bot.handlers.clips_common import DUMMY_CALLBACK_VALUE

router = Router()


@router.error()
async def on_error_shutdown(_: ErrorEvent, on_failure: Callable[[], Awaitable[None]]) -> None:
    logger.exception('Handler exception')
    await on_failure()


@router.callback_query(F.data == DUMMY_CALLBACK_VALUE)
async def on_dummy_button(callback: CallbackQuery) -> None:
    await callback.answer()


@router.message(Command('start'))
async def on_start_send_menu(message: Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Clips')],
        ],
        resize_keyboard=True,
        input_field_placeholder='Choose an option...',
    )
    await message.answer(
        text='Menu loaded',
        reply_markup=keyboard,
    )
