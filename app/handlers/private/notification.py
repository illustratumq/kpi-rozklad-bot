from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from app.keyboards.inline.pagination import notify_kb, switch_notify, notify_cb
from app.schedule.decorator import ScheduleDecorator
from database.services.repos import UserRepo, GroupRepo, LectureRepo, NotifyRepo

DAYS = ['Пн', 'Вв', 'Ср', 'Чт', 'Пт', 'Сб']


async def notify_cmd(call: CallbackQuery, callback_data: dict, user_db: UserRepo, group_db: GroupRepo,
                     lecture_db: LectureRepo):
    user = await user_db.get_user(call.from_user.id)
    group = await group_db.get_group(user.group_id)
    week = int(callback_data['week'])
    day = int(callback_data['day'])
    decorator = ScheduleDecorator(group.schedule)
    lecture_text = ScheduleDecorator(group.schedule).day(DAYS[day], week, recompose=True)
    lectures = []
    for pair in decorator.group.lectures(decorator.group.day(DAYS[day], week)):
        lecture = await lecture_db.get_lecture(group_id=group.group_id, name=pair['name'], tag=pair['tag'])
        lectures.append(lecture.lecture_id)
    await call.message.edit_text(text=lecture_text, reply_markup=notify_kb(lectures, group.group_id, week, day))


async def switch_notification(call: CallbackQuery, callback_data: dict, user_db: UserRepo, group_db: GroupRepo,
                              lecture_db: LectureRepo, notify_db: NotifyRepo):
    user = await user_db.get_user(call.from_user.id)
    group = await group_db.get_group(user.group_id)
    week = int(callback_data['week'])
    day = int(callback_data['day'])
    action = callback_data['action']
    lecture_id = int(callback_data['lecture_id'])
    notify = await notify_db.get_user_notify(lecture_id, user.user_id)
    if notify is None:
        notify = await notify_db.add(
            user_id=user.user_id, group_id=group.group_id, lecture_id=lecture_id
        )
    if action == 'on':
        await notify_db.update_notify(notify.notify_id, notification=True)
    elif action == 'off':
        await notify_db.update_notify(notify.notify_id, notification=False)
    lecture = await lecture_db.get_lecture_by_id(lecture_id)
    switch = not notify.notification
    marker = ScheduleDecorator.get_marker(lecture.tag)
    if notify.notification:
        current_setting = 'включено ✔'
    else:
        current_setting = 'виключено'
    text = (
        f'Ти хочеш налаштувати сповіщення на пару\n\n'
        f'<b>{marker} {lecture.name}</b>\n\n'
        f'Сповіщення: <b>{current_setting}</b>\n\n'
        f'Для цього надішли обери опцію нижче 👇'
    )
    await call.message.edit_text(text, reply_markup=switch_notify(lecture_id, group.group_id, week, day, switch))


def setup(dp: Dispatcher):
    dp.register_callback_query_handler(switch_notification, notify_cb.filter(), state='*')
