from aiogram.dispatcher.filters import BoundFilter
from aiogram.types import Message


class IsLinkValid(BoundFilter):
    async def check(self, msg: Message, *args: ...) -> bool:
        return any(['zoom' in msg.text, 'meet' in msg.text])
