from aiogram import Dispatcher

from app.handlers.admin import admin, message, info


def setup(dp: Dispatcher):
    admin.setup(dp)
    info.setup(dp)
    message.setup(dp)
