from typing import Any

from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware
from aiogram.types.base import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from database.services.repos import *


class DatabaseMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ['error', 'update']

    def __init__(self, session_pool: sessionmaker) -> None:
        self.session_pool = session_pool
        super().__init__()

    async def pre_process(self, obj: TelegramObject, data: dict, *args: Any) -> None:
        session: AsyncSession = self.session_pool()
        data['user_db'] = UserRepo(session)
        data['group_db'] = GroupRepo(session)
        data['lecture_db'] = LectureRepo(session)
        data['notify_db'] = NotifyRepo(session)
        data['session'] = session

    async def post_process(self, obj: TelegramObject, data: dict, *args: Any) -> None:
        if session := data.get('session', None):
            session: AsyncSession
            await session.close()
