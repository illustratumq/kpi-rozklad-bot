from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message, CallbackQuery


class IsGroup(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        chat_types = (
            types.ChatType.GROUP,
            types.ChatType.SUPERGROUP
        )
        if isinstance(upd, Message):
            return upd.chat.type in chat_types
        else:
            return upd.message.chat.type in chat_types


class IsPrivate(BoundFilter):
    async def check(self, upd: Message | CallbackQuery, *args: ...) -> bool:
        chat_types = (
            types.ChatType.PRIVATE
        )
        if isinstance(upd, Message):
            return upd.chat.type in chat_types
        else:
            return upd.message.chat.type in chat_types
