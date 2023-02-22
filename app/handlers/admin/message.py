from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, ContentTypes

from app.handlers.admin.admin import admin_msg
from app.keyboards.reply.admin import *
from app.states.states import MessageSG
from database.services.repos import UserRepo


async def message_cmd(msg: Message):
    text = (
        '1) Відправ текст який побачать користувачі'
    )
    await msg.answer(text, reply_markup=cancel_kb)
    await MessageSG.Text.set()


async def save_text(msg: Message, state: FSMContext):
    await msg.delete()
    await state.update_data(text=msg.html_text)
    await compose_post(state, msg)
    await msg.answer('2) Відправ фото для посту або пропусти цей крок', reply_markup=edit_kb)
    await MessageSG.Photo.set()


async def save_photo(msg: Message, state: FSMContext):
    if msg.text != Buttons.admin.skip:
        await msg.delete()
        await state.update_data(file_id=msg.photo[-1].file_id)
        await compose_post(state, msg)
    await msg.answer('3) Відправ текст для кнопки або пропусти цей крок', reply_markup=edit_kb)
    await MessageSG.ButtonText.set()


async def save_button(msg: Message, state: FSMContext):
    if msg.text != Buttons.admin.skip:
        await msg.delete()
        await compose_post(state, msg)
        await state.update_data(button_text=msg.text)
    await msg.answer('4) Відправ посилання для кнопки', reply_markup=edit_kb)
    await MessageSG.ButtonUrl.set()


async def save_post(msg: Message, state: FSMContext):
    if msg.text != Buttons.admin.skip:
        await msg.delete()
        await state.update_data(button_url=msg.text)
        await compose_post(state, msg)
    await msg.answer('5) Підтверди відпраку повідомлень', reply_markup=confirm_kb)
    await MessageSG.Confirm.set()


async def send_post(msg: Message, state: FSMContext, user_db: UserRepo):
    users = await user_db.get_all()
    count = 0
    blocked = 0
    for user in users:
        try:
            await compose_post(state, msg, user.user_id)
            count += 1
        except:
            blocked += 1
    await msg.answer(f'Пост відправлений {count} юзерам, заблокували бота {blocked}')
    await state.finish()
    await admin_msg(msg, state)


def setup(dp: Dispatcher):
    dp.register_message_handler(message_cmd, text=Buttons.admin.create_message, state='*')
    dp.register_message_handler(message_cmd, text=Buttons.admin.edit, state='*')
    dp.register_message_handler(save_text, state=MessageSG.Text)
    dp.register_message_handler(save_photo, state=MessageSG.Photo, content_types=ContentTypes.PHOTO)
    dp.register_message_handler(save_photo, state=MessageSG.Photo)
    dp.register_message_handler(save_post, state=MessageSG.ButtonText, text=Buttons.admin.skip)
    dp.register_message_handler(save_button, state=MessageSG.ButtonText)
    dp.register_message_handler(save_post, state=MessageSG.ButtonUrl)
    dp.register_message_handler(send_post, state=MessageSG.Confirm, text=Buttons.admin.send)


async def compose_post(state: FSMContext, msg: Message, user_id: int = None):
    data = await state.get_data()
    keys = list(data.keys())
    text = data['text']
    answer = dict(text=text)
    func = msg.answer if not user_id else msg.bot.send_message
    if 'last_msg_id' in keys and not user_id:
        await msg.bot.delete_message(msg.from_user.id, data['last_msg_id'])
    if 'file_id' in keys:
        file_id = data['file_id']
        answer.pop('text')
        answer.update(photo=file_id, caption=text)
        func = msg.answer_photo if not user_id else msg.bot.send_photo
    if 'button_text' in keys:
        button_text = data['button_text']
        button_url = data['button_url']
        reply_markup = create_url_button(button_text, button_url)
        answer.update(reply_markup=reply_markup)
    if user_id:
        answer.update(chat_id=user_id)
        await func(**answer)
        return
    msg = await func(**answer)
    await state.update_data(last_msg_id=msg.message_id)
