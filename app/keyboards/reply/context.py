from app.keyboards.reply.base import *

today_kb = ReplyKeyboardMarkup(
    row_width=1,
    resize_keyboard=True,
    one_time_keyboard=True,
    keyboard=[
        [KeyboardButton(Buttons.today.info)],
        [KeyboardButton(Buttons.today.back)]
    ]
)


def group_kb(group_chat: bool = False):
    return ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=False,
        keyboard=[
            [KeyboardButton(Buttons.group.info)],
            [KeyboardButton(Buttons.group.change),
             KeyboardButton(Buttons.group.del_chat if group_chat else Buttons.group.add_chat)],
            [KeyboardButton(Buttons.today.back)]
        ]
    )


def setting_kb(notify: bool, mark: bool):
    return ReplyKeyboardMarkup(
        row_width=1,
        resize_keyboard=True,
        one_time_keyboard=False,
        keyboard=[
            [KeyboardButton(Buttons.settings.notify_off if notify else Buttons.settings.notify_on)],
            [KeyboardButton(Buttons.settings.mark_off if mark else Buttons.settings.mark_on)],
            [KeyboardButton(Buttons.menu.back)]
        ]
    )