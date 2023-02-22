import random

import emoji
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, CallbackQuery, BotCommand, BotCommandScopeChat

from app.filters.group import IsGroup
from app.handlers.group.emojies import emoji_list
from app.keyboards.inline.chat import chat_menu_kb, chat_cb
from app.schedule.decorator import ScheduleDecorator
from app.schedule.timer import Current
from database.services.repos import UserRepo, GroupRepo


DAYS = ['Пн', 'Вв', 'Ср', 'Чт', 'Пт', 'Сб']


async def group_chat_menu(msg: Message, group_db: GroupRepo):
    await msg.delete()
    group = await group_db.get_group_by_chat(msg.chat.id)
    text = (
        'Для модерації в чаті використовуй кнопки нижче:\n\n'
        '<b>Використовувати цей чат як груповий</b> - "💬"\n\n'
        '<b>Розклад на сьогодні</b> - "📚"\n\n'
        '<b>Відмітити всіх в чаті</b> - "@"'
    )
    if group:
        text = f'Група {group.name}\n\n' + text
    await msg.answer(text, reply_markup=chat_menu_kb(msg.from_user.id, msg.chat.id))
    default_commands = [
        BotCommand('group', 'Показати меню'),
    ]
    await msg.bot.set_my_commands(
        commands=default_commands,
        scope=BotCommandScopeChat(chat_id=msg.chat.id)
    )


async def close_menu(call: CallbackQuery):
    await call.message.delete()


async def use_group_chat(call: CallbackQuery, user_db: UserRepo, group_db: GroupRepo):
    user = await user_db.get_user(call.from_user.id)
    if not user:
        await call.answer('Ти не зареєстрований в боті', show_alert=True)
        return
    group = await group_db.get_group(user.group_id)
    if not group:
        await call.answer('Ти не обрав групу', show_alert=True)
    await call.answer()
    await group_db.update_group(group.group_id, chat_id=call.message.chat.id)
    text = (
        f'📚 Тепер ця група буде використовуватись як груповий чат {group.name}. '
        f'Сповіщення будуть приходити за 5 хв до початку пари'
    )
    await call.message.answer(text)
    await call.message.delete()


async def mark_all_users(call: CallbackQuery, user_db: UserRepo, group_db: GroupRepo):
    user = await user_db.get_user(call.from_user.id)
    if not user:
        await call.answer('Ти не зареєстрований в боті', show_alert=True)
        return
    group = await group_db.get_group(user.group_id)
    if not group:
        await call.answer('Ти не обрав групу', show_alert=True)
    users = await user_db.get_users_by_group(group.group_id)
    await call.answer()
    string = ''
    count = 0
    for user in users:
        if user.mark:
            count += 1
            string += get_mention(user.user_id)
            if count % 4 == 0:
                count = 0
                await call.message.answer(string)
    if count > 0:
        await call.message.answer(string)
    await call.message.delete()


async def today_lectures_group(call: CallbackQuery, user_db: UserRepo, group_db: GroupRepo, timer: Current):
    user = await user_db.get_user(call.from_user.id)
    if not user:
        await call.answer('Ти не зареєстрований в боті', show_alert=True)
        return
    group = await group_db.get_group(user.group_id)
    if not group:
        await call.answer('Ти не обрав групу', show_alert=True)
    await call.answer()
    time = timer.current()
    lectures = ScheduleDecorator(group.schedule).day(DAYS[time.day], week=time.week, current=True)
    if lectures:
        await call.message.answer(lectures, disable_web_page_preview=True)
    await call.message.delete()


def setup(dp: Dispatcher):
    dp.register_message_handler(group_chat_menu, Command('group'), IsGroup(), state='*')
    dp.register_message_handler(group_chat_menu, Command('start'), IsGroup(), state='*')
    dp.register_callback_query_handler(close_menu, chat_cb.filter(action='close'), state='*')
    dp.register_callback_query_handler(use_group_chat, chat_cb.filter(action='chat'), state='*')
    dp.register_callback_query_handler(mark_all_users, chat_cb.filter(action='mark'), state='*')
    dp.register_callback_query_handler(today_lectures_group, chat_cb.filter(action='pair'), state='*')


def get_mention(user_id: int):
    emj = emoji.emojize(random.choice(emoji_list))
    while ':' in emj:
        emj = emoji.emojize(random.choice(emoji_list))
    return f"<a href='tg://user?id={user_id}'>{emj}</a>"
