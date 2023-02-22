from app.keyboards.inline.base import *

chat_cb = CallbackData('cht', 'action', 'user_id', 'chat_id')


def chat_menu_kb(user_id: int, chat_id: int):
    chat = chat_cb.new(action='chat', user_id=user_id, chat_id=chat_id)
    pair = chat_cb.new(action='pair', user_id=user_id, chat_id=chat_id)
    close = chat_cb.new(action='close', user_id=user_id, chat_id=chat_id)
    mark = chat_cb.new(action='mark', user_id=user_id, chat_id=chat_id)
    return InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [InlineKeyboardButton('💬', callback_data=chat),
             InlineKeyboardButton('📚', callback_data=pair),
             InlineKeyboardButton('@', callback_data=mark)],
            [InlineKeyboardButton('Закрити', callback_data=close)]
        ]
    )
