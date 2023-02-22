from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from app.handlers.private.link import add_link
from app.handlers.private.menu import start_cmd
from app.handlers.private.notification import notify_cmd
from app.keyboards import Buttons
from app.keyboards.inline.pagination import pagination_kb, pagination_cb
from app.keyboards.reply.context import today_kb
from app.keyboards.reply.menu import back_menu_kb
from app.schedule.decorator import ScheduleDecorator
from app.schedule.timer import Current
from database.services.repos import UserRepo, GroupRepo, LectureRepo

DAYS = ['Пн', 'Вв', 'Ср', 'Чт', 'Пт', 'Сб']
WEEK = {1: 'Перший', 2: 'Другий'}


async def current_week(msg: Message, user_db: UserRepo, group_db: GroupRepo, timer: Current):
    time = timer.current()
    await msg.answer(f'Розклад на {WEEK[time.week]} тиждень', reply_markup=back_menu_kb)
    user = await user_db.get_user(msg.from_user.id)
    group = await group_db.get_group(user.group_id)
    reply_markup = pagination_kb(group.group_id, week=time.week, day=0)
    lectures = ScheduleDecorator(group.schedule).day(day_name=DAYS[0], week=time.week)
    if lectures:
        await msg.answer(lectures, reply_markup=reply_markup, disable_web_page_preview=True)


async def other_week(msg: Message, user_db: UserRepo, group_db: GroupRepo, timer: Current):
    time = timer.current()
    await msg.answer(f'Розклад на {WEEK[time.second_week]} тиждень', reply_markup=back_menu_kb)
    user = await user_db.get_user(msg.from_user.id)
    group = await group_db.get_group(user.group_id)
    reply_markup = pagination_kb(group.group_id, week=time.second_week, day=0)
    lectures = ScheduleDecorator(group.schedule).day(day_name=DAYS[0], week=time.second_week)
    if lectures:
        await msg.answer(lectures, reply_markup=reply_markup, disable_web_page_preview=True)


async def today_lectures(msg: Message, user_db: UserRepo, group_db: GroupRepo, timer: Current):
    user = await user_db.get_user(msg.from_user.id)
    group = await group_db.get_group(user.group_id)
    time = timer.current()
    lectures = ScheduleDecorator(group.schedule).day(DAYS[time.day], week=time.week, current=True)
    if lectures:
        await msg.answer(lectures, disable_web_page_preview=True, reply_markup=today_kb)


async def next_day_lectures(msg: Message, user_db: UserRepo, group_db: GroupRepo, timer: Current):
    user = await user_db.get_user(msg.from_user.id)
    group = await group_db.get_group(user.group_id)
    time = timer.current()
    day = time.day + 1 if time.day != 6 else 0
    lectures = ScheduleDecorator(group.schedule).day(DAYS[day], week=time.week)
    if lectures:
        await msg.answer(lectures, disable_web_page_preview=True, reply_markup=today_kb)


async def pagination_schedule(call: CallbackQuery, callback_data: dict, user_db: UserRepo, group_db: GroupRepo,
                              lecture_db: LectureRepo, state: FSMContext):
    user = await user_db.get_user(call.from_user.id)
    group = await group_db.get_group(user.group_id)
    week = int(callback_data['week'])
    day = int(callback_data['day'])
    action = callback_data['action']
    if action == 'close':
        await call.message.delete_reply_markup()
        await start_cmd(call.message, user_db, state)
        return
    elif action == 'link':
        await add_link(call, callback_data, user_db, group_db, lecture_db)
        return
    elif action == 'notify':
        await notify_cmd(call, callback_data, user_db, group_db, lecture_db)
        return
    lectures = ScheduleDecorator(group.schedule).day(DAYS[day], week)
    reply_markup = pagination_kb(group.group_id, week, day)
    if lectures:
        await call.message.edit_text(lectures, disable_web_page_preview=True, reply_markup=reply_markup)


def setup(dp: Dispatcher):
    dp.register_message_handler(current_week, text=Buttons.menu.current_week, state='*')
    dp.register_message_handler(other_week, text=Buttons.menu.next_week, state='*')
    dp.register_message_handler(today_lectures, text=Buttons.menu.today, state='*')
    dp.register_message_handler(next_day_lectures, text=Buttons.menu.next_day, state='*')
    dp.register_callback_query_handler(pagination_schedule, pagination_cb.filter(), state='*')
