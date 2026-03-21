from aiogram import Router

from general_bot.handlers.clips_fetch import router as clips_fetch_router
from general_bot.handlers.clips_store import router as clips_store_router
from general_bot.handlers.core import router as core_router

router = Router()
router.include_router(core_router)
router.include_router(clips_fetch_router)
router.include_router(clips_store_router)
