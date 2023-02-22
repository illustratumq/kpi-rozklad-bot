from aiogram import Dispatcher
from aiogram.types import Message

from app.keyboards import Buttons
from app.keyboards.reply.context import today_kb, group_kb
from app.keyboards.reply.menu import back_menu_kb
from database.services.repos import GroupRepo, UserRepo


async def notify_and_links(msg: Message):
    text = (
        '<b>ℹ Як використовувати бота максимум ефективно?</b>\n\n'
        '🔸 <b>Сповіщення</b>\n\n'
        'Щоб отримувати сповіщення на будь-яку пару за 5 хв до її початку, перейди в розділ '
        '<b>"Цей тиждень/Наступний"</b>, знайди пару, яка тебе цікавить, натисни кнопку '
        '<b>"🔔 Сповіщення"</b>, та обери опцію увімкнути або вимкнути. За замовчуванням всі '
        'сповіщення увімкнені. Для того щоб увімкнути/вимкнути всі сповіщення одразу, перейди в розділ '
        f'<b>"{Buttons.menu.settings}"</b> та обери відповідну опцію.\n\n'
        f'🔸 <b>Посилання</b>\n\n'
        f'Якщо хочеш зберегти посилання на пару в боті, перейди в розділ <b>"Цей тиждень/Наступний"</b> '
        f'знайди пару, яка тебе цікавить, натисни кнопку <b> "🔗 Посилання"</b>, і надішли лінк, з однієї '
        f'з платформ Zoom бо GoogleMeet. Видалити посилання можна в тому ж розділі.\n\n'
        f'💭 Незабувай ділитись @kpi_rozklad_bot з друзями. Успіхів!'
    )
    await msg.answer(text, reply_markup=today_kb)


async def groups_and_chats(msg: Message, user_db: UserRepo, group_db: GroupRepo):
    user = await user_db.get_user(msg.from_user.id)
    group = await group_db.get_group(user.group_id)
    text = (
        '<b>ℹ Як отримувати сповіщення в груповому чаті?</b>\n\n'
        '🔸 <b>Груповий чат</b>\n\n'
        'Щоб отримувати сповіщення в телеграм групі треба виконати декілька простих умов:\n\n'
        '- Додати бота в чат групи\n'
        '- Надати боту права адміністратора\n'
        '- Додати чат в налаштуваннях <b>"Моя група🎓"</b>\n\n'
        '🕐 Після цього сповіщення будуть приходити в чат за 5 хв до початку пари.\n\n'
        'Видалити чат можна в тому ж розділі. Якщо бот не зможе відправити повідомлення в чат,'
        'інформація про груповий чат буде видалена з бази даних.\n\n'
        '💭 Незабувай ділитись @kpi_rozklad_bot з друзями. Успіхів!'
    )
    await msg.answer(text, reply_markup=group_kb(group.chat_id is not None))


async def info_user_cmd(msg: Message):
    await msg.answer(read_message(), reply_markup=back_menu_kb, disable_web_page_preview=True)


def setup(dp: Dispatcher):
    dp.register_message_handler(notify_and_links, text=Buttons.today.info, state='*')
    dp.register_message_handler(groups_and_chats, text=Buttons.group.info, state='*')
    dp.register_message_handler(info_user_cmd, text=Buttons.menu.news, state='*')


def read_message():
    with open('app/handlers/admin/message.txt', 'r', encoding='utf-8') as file:
        return file.read()