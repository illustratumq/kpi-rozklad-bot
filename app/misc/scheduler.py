from aiogram import Bot
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.base import BaseExecutor
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from sqlalchemy.orm import sessionmaker
from tzlocal import get_localzone

from app.config import Config
from app.schedule.timer import Current


def _configure_executors() -> dict[str, BaseExecutor]:
    return {
        'threadpool': ThreadPoolExecutor(),
        'default': AsyncIOExecutor()
    }


def compose_scheduler(config: Config, bot: Bot,
                      session: sessionmaker, timer: Current) -> ContextSchedulerDecorator:
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(
        executors=_configure_executors(),
        timezone=str(get_localzone())
    ))
    scheduler.ctx.add_instance(timer, Current)
    scheduler.ctx.add_instance(bot, Bot)
    scheduler.ctx.add_instance(session, sessionmaker)
    scheduler.ctx.add_instance(config, Config)
    scheduler.ctx.add_instance(scheduler, ContextSchedulerDecorator)
    return scheduler
