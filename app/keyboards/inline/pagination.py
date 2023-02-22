from app.keyboards.inline.base import *

pagination_cb = CallbackData('pg', 'group_id', 'week', 'day', 'action')
link_cb = CallbackData('lk', 'lecture_id', 'week', 'day', 'action')
notify_cb = CallbackData('nt', 'lecture_id', 'week', 'day', 'action')


def pagination_kb(group_id: str, week: int, day: int):
    prev_day = pagination_cb.new(group_id=group_id, week=week, day=(day - 1) % 6, action='prev')
    next_day = pagination_cb.new(group_id=group_id, week=week, day=(day + 1) % 6, action='next')
    close = pagination_cb.new(group_id=group_id, week=week, day=day, action='close')
    link = pagination_cb.new(group_id=group_id, week=week, day=day, action='link')
    notify = pagination_cb.new(group_id=group_id, week=week, day=day, action='notify')
    keyboard = [
        [
            InlineKeyboardButton('🔗 Посилання', callback_data=link),
            InlineKeyboardButton('🔔 Сповіщення', callback_data=notify)
        ],
        [
          InlineKeyboardButton('⬅', callback_data=prev_day),
          InlineKeyboardButton('Назад', callback_data=close),
          InlineKeyboardButton('➡', callback_data=next_day)
        ]
    ]
    return InlineKeyboardMarkup(
        row_width=3,
        inline_keyboard=keyboard
    )


def notify_kb(lectures_id: list, group_id: str, week: int, day: int):
    cb = [notify_cb.new(lecture_id=lectures_id[i], action='select', week=week, day=day)
          for i in range(len(lectures_id))]
    close = pagination_cb.new(group_id=group_id, week=week, day=day, action='prev')
    keyboard = [[InlineKeyboardButton(str(i + 1), callback_data=cb[i]) for i in range(len(lectures_id))],
                [InlineKeyboardButton('◀ Назад', callback_data=close)]]
    return InlineKeyboardMarkup(
        row_width=len(lectures_id),
        inline_keyboard=keyboard
    )


def switch_notify(lecture_id: int, group_id: str, week: int, day: int, switch: bool):
    on = notify_cb.new(lecture_id=lecture_id, week=week, day=day, action='on')
    off = notify_cb.new(lecture_id=lecture_id, week=week, day=day, action='off')
    close = pagination_cb.new(group_id=group_id, week=week, day=day, action='prev')
    return InlineKeyboardMarkup(
        row_width=2,
        inline_keyboard=[
            [
                InlineKeyboardButton('🔔 Увімкнути', callback_data=on) if switch else
                InlineKeyboardButton('🔕 Вимкнути', callback_data=off)
            ],
            [InlineKeyboardButton('◀ Назад', callback_data=close)]
        ]
    )


def link_kb(lectures_id: list, group_id: str, week: int, day: int):
    cb = [link_cb.new(lecture_id=lectures_id[i], action='add', week=week, day=day) for i in range(len(lectures_id))]
    close = pagination_cb.new(group_id=group_id, week=week, day=day, action='prev')
    keyboard = [[InlineKeyboardButton(str(i+1), callback_data=cb[i]) for i in range(len(lectures_id))],
                [InlineKeyboardButton('◀ Назад', callback_data=close)]]
    return InlineKeyboardMarkup(
        row_width=len(lectures_id),
        inline_keyboard=keyboard
    )


def remove_link(lecture_id: int, group_id: str, week: int, day: int):
    cb = link_cb.new(lecture_id=lecture_id, action='delete', week=week, day=day)
    close = pagination_cb.new(group_id=group_id, week=week, day=day, action='prev')
    keyboard = [
        [InlineKeyboardButton('Видалити посилання', callback_data=cb)],
        [InlineKeyboardButton('◀ Назад', callback_data=close)]
    ]
    return InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=keyboard
    )
