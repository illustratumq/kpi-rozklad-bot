from app.keyboards.reply.base import *


def menu_kb(night: bool = False, admin: bool = False):
    keyboard = [
        [
            KeyboardButton(Buttons.menu.today) if not night else KeyboardButton(Buttons.menu.next_day)
        ],
        [
            KeyboardButton(Buttons.menu.current_week),
            KeyboardButton(Buttons.menu.next_week)
        ],
        [
            KeyboardButton(Buttons.menu.news),
            KeyboardButton(Buttons.menu.my_group)
        ],
        [
            KeyboardButton(Buttons.menu.settings)
        ]
    ]
    if admin:
        keyboard[-1].append(KeyboardButton(Buttons.menu.admin))
    return ReplyKeyboardMarkup(
        row_width=2,
        resize_keyboard=True,
        one_time_keyboard=True,
        keyboard=keyboard
    )


back_menu_kb = ReplyKeyboardMarkup(
    row_width=1,
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [
            KeyboardButton(Buttons.menu.back)
        ]
    ]
)
