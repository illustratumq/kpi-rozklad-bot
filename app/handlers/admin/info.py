from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.admin import cancel_kb, admin_kb
from app.states.states import InfoSG


async def info_cmd(msg: Message):
    text = (
        'Щоб створити нове повідомлення, надішли текст.\n\n'
        f'Поточне повідомлення:\n\n{read_message()}'
    )
    await msg.answer(text, reply_markup=cancel_kb)
    await InfoSG.Input.set()


async def update_info(msg: Message, state: FSMContext):
    write_message(msg.html_text)
    await msg.answer('Текст успішно збережено', reply_markup=admin_kb)
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_message_handler(info_cmd, IsAdminFilter(), text=Buttons.admin.news, state='*')
    dp.register_message_handler(update_info, IsAdminFilter(), state=InfoSG.Input)


def write_message(text: str):
    with open('app/handlers/admin/message.txt', 'w', encoding='utf-8') as file:
        file.write(text)


def read_message():
    with open('app/handlers/admin/message.txt', 'r', encoding='utf-8') as file:
        return file.read()
