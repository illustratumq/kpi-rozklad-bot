from aiogram import Dispatcher

from app.handlers.group import chat_menu


def setup(dp: Dispatcher):
    chat_menu.setup(dp)
