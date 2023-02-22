from aiogram import Dispatcher

from app.handlers import private, admin, group


def setup(dp: Dispatcher):
    private.setup(dp)
    admin.setup(dp)
    group.setup(dp)