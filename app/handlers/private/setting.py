from aiogram import Dispatcher
from aiogram.types import Message

from app.keyboards import Buttons
from app.keyboards.reply.context import setting_kb
from database.services.repos import UserRepo


async def setting_cmd(msg: Message, user_db: UserRepo):
    user = await user_db.get_user(msg.from_user.id)
    true = 'Включено ✔'
    false = 'Виключено'
    text = (
        'Поточні налаштування\n\n'
        f'Сповіщення про пари: {true if user.notification else false}\n'
        f'Відмітка в груповому чаті: {true if user.mark else false}'
    )
    await msg.answer(text, reply_markup=setting_kb(user.notification, user.mark))


async def notify_on(msg: Message, user_db: UserRepo):
    await msg.answer('Сповіщення на всі пари включено')
    await user_db.update_user(user_id=msg.from_user.id, notification=True)
    await setting_cmd(msg, user_db)


async def notify_off(msg: Message, user_db: UserRepo):
    await msg.answer('Сповіщення на всі пари виключено')
    await user_db.update_user(user_id=msg.from_user.id, notification=False)
    await setting_cmd(msg, user_db)


async def mark_on(msg: Message, user_db: UserRepo):
    await msg.answer('Тебе знову можуть відмічати в груповому чаті')
    await user_db.update_user(user_id=msg.from_user.id, mark=True)
    await setting_cmd(msg, user_db)


async def mark_off(msg: Message, user_db: UserRepo):
    await msg.answer('Тебе більше не можуть відмічати в груповому чаті')
    await user_db.update_user(user_id=msg.from_user.id, mark=False)
    await setting_cmd(msg, user_db)


def setup(dp: Dispatcher):
    dp.register_message_handler(setting_cmd, text=Buttons.menu.settings, state='*')
    dp.register_message_handler(notify_on, text=Buttons.settings.notify_on, state='*')
    dp.register_message_handler(notify_off, text=Buttons.settings.notify_off, state='*')
    dp.register_message_handler(mark_on, text=Buttons.settings.mark_on, state='*')
    dp.register_message_handler(mark_off, text=Buttons.settings.mark_off, state='*')
