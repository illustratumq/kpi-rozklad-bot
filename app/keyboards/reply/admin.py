from app.keyboards.reply.base import *
from app.keyboards.inline.base import *


def create_url_button(text: str, url: str):
    return InlineKeyboardMarkup(row_width=1, inline_keyboard=[[InlineKeyboardButton(
        text=text, url=url
    )]])


admin_kb = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    one_time_keyboard=False,
    keyboard=[
        [KeyboardButton(Buttons.admin.statistic)],
        [KeyboardButton(Buttons.admin.create_message), KeyboardButton(Buttons.admin.news)],
        [KeyboardButton(Buttons.menu.back)]
    ]
)

cancel_bt = [KeyboardButton(Buttons.admin.cancel)]

cancel_kb = ReplyKeyboardMarkup(
    row_width=1,
    resize_keyboard=True,
    one_time_keyboard=False,
    keyboard=[cancel_bt]
)

edit_kb = ReplyKeyboardMarkup(
    row_width=1,
    resize_keyboard=True,
    one_time_keyboard=False,
    keyboard=[
        [KeyboardButton(Buttons.admin.edit),
         KeyboardButton(Buttons.admin.skip)], cancel_bt
    ]
)

confirm_kb = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    one_time_keyboard=False,
    keyboard=[
        [KeyboardButton(Buttons.admin.edit)],
        [KeyboardButton(Buttons.admin.send), KeyboardButton(Buttons.admin.cancel)]
    ]
)
