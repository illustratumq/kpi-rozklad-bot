from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.keyboards import Buttons
from app.keyboards.inline.inline import inline_kb
from app.keyboards.reply.context import group_kb
from app.schedule.decorator import ScheduleDecorator
from app.states.states import GroupSG
from database.services.repos import UserRepo, GroupRepo, LectureRepo, NotifyRepo


async def my_group(msg: Message, user_db: UserRepo, group_db: GroupRepo, lecture_db: LectureRepo):
    user = await user_db.get_user(msg.from_user.id)
    users = await user_db.get_users_by_group(user.group_id)
    group = await group_db.get_group(user.group_id)
    lectures = await lecture_db.get_lectures_by_group(group.group_id)
    labs = [lecture for lecture in lectures if lecture.tag == 'lab']
    prac = [lecture for lecture in lectures if lecture.tag == 'prac']
    lec = [lecture for lecture in lectures if lecture.tag == 'lec']
    group_chat = 'Не знайдено' if group.chat_id is None else f'Знайдено 🆔{group.chat_id}'
    text = (
        f'🎓 Твоя група {group.name} {group.faculty}\n\n'
        f'Відслідковують групу: {len(users)} студентів\n'
        f'Груповий чат: {group_chat}\n\n'
        f'<b>📆 В цьому семестрі ти маєш:</b>\n\n'
        f'{ScheduleDecorator.get_marker("lec")} {len(lec)} Лекцій\n'
        f'{ScheduleDecorator.get_marker("lab")} {len(labs)} Лабораторних\n'
        f'{ScheduleDecorator.get_marker("prac")} {len(prac)} Практичних\n'
    )
    await msg.answer(text, reply_markup=group_kb(group.chat_id is not None))


async def resolve_group(msg: Message, state: FSMContext):
    text = (
        '<b>Ти дійсно бажаєш змінити групу?</b>\n\n'
        'Попередні налаштування сповіщень будуть видалені. Для '
        'того щоб змінити групу <b>🔍 натисни на кнопку</b> нижче або повернись'
        ' в головне меню, щоб відмінити дію'
    )
    msg = await msg.answer(text, reply_markup=inline_kb)
    await state.update_data(last_msg_id=msg.message_id)
    await GroupSG.Group.set()


async def resave_group(msg: Message, group_db: GroupRepo, user_db: UserRepo,
                       lecture_db: LectureRepo, notify_db: NotifyRepo, state: FSMContext):
    data = await state.get_data()
    last_msg_id = data['last_msg_id']
    group_name = msg.text
    group = await group_db.get_group_by_name(group_name)
    if group is None:
        await msg.answer('Такої групи немає, спробуй ще раз')
        return
    await msg.bot.delete_message(msg.from_user.id, last_msg_id)
    await user_db.update_user(msg.from_user.id, group_id=group.group_id)
    notifies = await notify_db.get_notify_by_user(msg.from_user.id)
    for notify in notifies:
        await notify_db.delete_notify(notify.notify_id)
    for lecture in await lecture_db.get_lectures_by_group(group.group_id):
        await notify_db.add(
            user_id=msg.from_user.id, group_id=group.group_id, lecture_id=lecture.lecture_id, notification=True
        )
    await my_group(msg, user_db, group_db, lecture_db)
    await state.finish()


async def add_group(msg: Message):
    text = (
        '💬 Щоб додати груповий чат, будь ласка додай бота в групу, та натисни команду '
        '/group в чаті'
    )
    await msg.answer(text)


async def delete_chat(msg: Message, group_db: GroupRepo, user_db: UserRepo):
    user = await user_db.get_user(msg.from_user.id)
    text = (
        '💬 Груповий чат видалено'
    )
    group = await group_db.get_group(user.group_id)
    chat_text = (
        f'{user.full_name} прибрав чат із списку групових'
    )
    await msg.bot.send_message(group.chat_id, chat_text)
    await group_db.update_group(user.group_id, chat_id=None)
    await msg.answer(text, reply_markup=group_kb(False))


def setup(dp: Dispatcher):
    dp.register_message_handler(my_group, text=Buttons.menu.my_group, state='*')
    dp.register_message_handler(resolve_group, text=Buttons.group.change, state='*')
    dp.register_message_handler(resave_group, state=GroupSG.Group)
    dp.register_message_handler(add_group, text=Buttons.group.add_chat, state='*')
    dp.register_message_handler(delete_chat, text=Buttons.group.del_chat, state='*')
