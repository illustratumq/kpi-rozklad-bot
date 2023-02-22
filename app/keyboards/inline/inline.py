from app.keyboards.inline.base import *

inline_kb = InlineKeyboardMarkup(
    row_width=1,
    inline_keyboard=[
        [InlineKeyboardButton(Buttons.menu.search_group, switch_inline_query_current_chat='')]
    ]
)
