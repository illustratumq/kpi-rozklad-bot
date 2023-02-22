from aiogram import Dispatcher

from app.handlers.private import menu
from app.handlers.private import schedule
from app.handlers.private import link
from app.handlers.private import notification
from app.handlers.private import group
from app.handlers.private import help
from app.handlers.private import setting


def setup(dp: Dispatcher):
    menu.setup(dp)
    schedule.setup(dp)
    link.setup(dp)
    notification.setup(dp)
    group.setup(dp)
    setting.setup(dp)
    help.setup(dp)