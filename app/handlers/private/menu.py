from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent

from app.config import Config
from app.filters.group import IsPrivate
from app.keyboards import Buttons
from app.keyboards.inline.inline import inline_kb
from app.keyboards.reply.menu import menu_kb
from app.schedule.timer import now
from app.states.states import AuthSG, GroupSG
from database.models import Group
from database.services.repos import UserRepo, GroupRepo, LectureRepo, NotifyRepo


async def authorization_message(msg: Message):
    text = (
        f'<b>📚 Привіт {msg.from_user.full_name}! Вітаю в боті КПІ Розклад.</b>\n\n'
        f'Це надійний інструмент, який допоможе тобі легко і швидко мати доступ до '
        f'розкладу. Основні фішки боту:\n\n'
        f'🔸 Увесь розклад <b>вже завантажений в базу даних</b>, а отже ніякої залежності '
        f'від сайту.\n\n'
        f'🔸 <b>Особисті та групові сповіщення</b>.\nТи можеш налаштувати сповіщення для кожної пари окремо, '
        f'або відключити їх у меню налаштувань. Додай бота в чат своєї групи, щоб отрмувати сповіщення разом '
        f'з одногрупниками.\n\n'
        f'🔸 <b>Посилання на пару в боті.</b>\nДодавай лінк на пару і більше ніколи не витрачай ча на його пошуки.\n\n'
        f'💭 Незабувай ділитись @kpi_rozklad_bot з друзями. Успіхів!'
    )
    await msg.answer(text, reply_markup=inline_kb)
    await AuthSG.Group.set()


async def save_group_and_user(msg: Message, user_db: UserRepo, group_db: GroupRepo,
                              lecture_db: LectureRepo, notify_db: NotifyRepo, state: FSMContext):
    group = await group_db.get_group_by_name(msg.text)
    if group is None:
        await msg.answer('Такої групи не існує 🫤')
        return

    await msg.answer(f'Ти обрав групу {group.name} ({group.faculty})', reply_markup=menu_kb(is_night(), is_admin(msg)))
    user = await user_db.add(
        user_id=msg.from_user.id,
        full_name=msg.from_user.full_name,
        mention=msg.from_user.url,
        group_id=group.group_id
    )
    for lecture in await lecture_db.get_lectures_by_group(group.group_id):
        await notify_db.add(
            user_id=user.user_id, group_id=group.group_id, lecture_id=lecture.lecture_id,  notification=True
        )
    await state.finish()


async def start_cmd(msg: Message, user_db: UserRepo, state: FSMContext):
    await state.finish()
    if not msg.from_user.is_bot:
        user = await user_db.get_user(msg.from_user.id)
        if user is None:
            await authorization_message(msg)
            return
    await msg.answer('Мої вітаннячка', reply_markup=menu_kb(is_night(), is_admin(msg)))


def setup(dp: Dispatcher):
    dp.register_message_handler(start_cmd, CommandStart(), IsPrivate(), state='*')
    dp.register_message_handler(start_cmd, text=Buttons.menu.back, state='*')
    dp.register_message_handler(save_group_and_user, state=AuthSG.Group)
    dp.register_inline_handler(inline_group_search, state=[AuthSG.Group, GroupSG.Group])
    dp.register_inline_handler(inline_non_state, state='*')


async def inline_non_state(query: InlineQuery):
    results = [
        InlineQueryResultArticle(
            id='None',
            title='💭 Поділитись ботом',
            description='Натисни щоб відправити посилання на бота',
            input_message_content=InputTextMessageContent(
                message_text='📚 Бот з розкладом КПІ @kpi_rozklad_bot'
            )
        )
    ]
    await query.answer(results=results)


async def inline_group_search(query: InlineQuery, group_db: GroupRepo):
    query_text = str(query.query)
    if query_text == '':
        query_text = 'Д'
    groups = await group_db.get_all()
    results = []
    count = 0
    for group in groups:
        if count == 5:
            break
        group_name = group.name.lower()
        if group_name.startswith(query_text.lower()) or group_name.replace('-', '').startswith(query_text.lower()):
            results.append(create_article(group))
            count += 1
    await query.answer(results, is_personal=True)


def create_article(group: Group):
    return InlineQueryResultArticle(
        id=group.group_id,
        title=group.name,
        description=group.faculty,
        input_message_content=InputTextMessageContent(
            message_text=group.name
        )
    )


def is_night():
    return 17 <= now().hour < 24


def is_admin(msg: Message):
    config = Config.from_env()
    return msg.from_user.id in config.bot.admin_ids
