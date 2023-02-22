from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from app.filters.href import IsLinkValid
from app.keyboards.inline.pagination import link_kb, link_cb, remove_link
from app.schedule.decorator import ScheduleDecorator
from app.states.states import LinkSG
from database.services.repos import UserRepo, GroupRepo, LectureRepo

DAYS = ['Пн', 'Вв', 'Ср', 'Чт', 'Пт', 'Сб']


async def add_link(call: CallbackQuery, callback_data: dict, user_db: UserRepo, group_db: GroupRepo,
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
    await call.message.edit_text(text=lecture_text, reply_markup=link_kb(lectures, group.group_id, week, day))


async def input_link(call: CallbackQuery, callback_data: dict, user_db: UserRepo, group_db: GroupRepo,
                     lecture_db: LectureRepo, state: FSMContext):
    user = await user_db.get_user(call.from_user.id)
    group = await group_db.get_group(user.group_id)
    week = int(callback_data['week'])
    day = int(callback_data['day'])
    lecture_id = int(callback_data['lecture_id'])
    lecture = await lecture_db.get_lecture_by_id(lecture_id)
    action = callback_data['action']
    marker = ScheduleDecorator.get_marker(lecture.tag)
    if action == 'delete':
        schedule = ScheduleDecorator(group.schedule).delete_url(name=lecture.name, tag=lecture.tag)
        await group_db.update_group(group.group_id, schedule=schedule)
        await lecture_db.update_lecture(lecture_id=lecture_id, url=None)
        await call.message.edit_text(f'Посилання для\n\n<b>{marker} {lecture.name}</b>\n\nбуло видалено',
                                     reply_markup=link_kb([], group.group_id, week, day))
        return
    if lecture.url:
        exist_url = f'\n🔗 {lecture.url}\n\n'
        action = 'замінити'
        reply_markup = remove_link(lecture_id, group.group_id, week, day)
    else:
        exist_url = '\n\n'
        action = 'додати'
        reply_markup = link_kb([], group.group_id, week, day)
    text = (
        f'Ти хочеш {action} посилання на пару\n\n<b>{marker} {lecture.name}</b>{exist_url}'
        f'Для цього надішли його текстовим повідомленням. Зауваж, приймаються тільки посилання з '
        f'GoogleMeet та Zoom 👇'
    )
    msg = await call.message.edit_text(text, reply_markup=reply_markup)
    await LinkSG.Input.set()
    await state.update_data(lecture_id=lecture_id, day=day, week=week, last_msg_id=msg.message_id,
                            group_id=group.group_id)


async def save_link(msg: Message, state: FSMContext, lecture_db: LectureRepo, group_db: GroupRepo):
    data = await state.get_data()
    group_id = data['group_id']
    lecture_id = data['lecture_id']
    last_msg_id = data['last_msg_id']
    week = int(data['week'])
    day = int(data['day'])
    group = await group_db.get_group(group_id)
    lecture = await lecture_db.get_lecture_by_id(lecture_id)
    schedule = ScheduleDecorator(group.schedule).update_url(name=lecture.name, tag=lecture.tag, url=msg.text)
    await group_db.update_group(group_id, schedule=schedule)
    await lecture_db.update_lecture(lecture_id, url=msg.text)
    marker = ScheduleDecorator.get_marker(lecture.tag)
    text = (
        f'Посилання збережено ✅\n\n<b>{marker} {lecture.name}</b>\n'
        f'🔗 {lecture.url}'
    )
    await msg.bot.edit_message_reply_markup(msg.from_user.id, last_msg_id, reply_markup=None)
    await msg.answer(text, reply_markup=link_kb([], group_id, week, day))
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_callback_query_handler(input_link, link_cb.filter(), state='*')
    dp.register_message_handler(save_link, IsLinkValid(), state=LinkSG.Input)
