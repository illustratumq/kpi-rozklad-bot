import os
from datetime import timedelta
from PIL import Image, ImageDraw, ImageFont
import matplotlib
import matplotlib.pyplot as plt
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import Message, InputFile
from babel.dates import format_datetime
from matplotlib.axes import Axes

from app.filters import IsAdminFilter
from app.keyboards import Buttons
from app.keyboards.reply.admin import admin_kb
from app.schedule.timer import now
from database.models.base import TimedBaseModel
from database.services.repos import UserRepo, GroupRepo

matplotlib.use('TkAgg')


async def admin_msg(msg: Message, state: FSMContext):
    await state.finish()
    await msg.answer('Мої вітаннячка', reply_markup=admin_kb)


async def admin_statistic(msg: Message, user_db: UserRepo, group_db: GroupRepo):
    users = await user_db.get_all()
    groups = list(set([await group_db.get_group(user.group_id) for user in users]))
    chats = [group for group in groups if group.chat_id]
    faculties = list(set([(await group_db.get_group(group.group_id)).faculty for group in groups]))
    current = format_datetime(now(), locale='uk_UA', format='medium')
    text = (
        f'Статистика станом на {current}\n\n'
        f'<b>👾 Користувачів в боті:</b> {len(users)}\n'
        f'<b>🎓 Груп:</b> {len(groups)}\n'
        f'<b>💬 Чатів:</b> {len(chats)}\n'
        f'<b>📚 Факультетів:</b> {len(faculties)}'
    )
    fig, ax = plt.subplots(figsize=(8, 6))
    plot_data(users, 'Користувачі', 'gold', 1, ax, fig)
    plot_data(chats, 'Чати', 'royalblue', 2, ax, fig)
    plt.savefig('statistic.png')
    await msg.answer_photo(photo=InputFile('statistic.png'), caption=text)
    os.remove('statistic.png')


def setup(dp: Dispatcher):
    dp.register_message_handler(admin_msg, Command('admin'), IsAdminFilter(), state='*')
    dp.register_message_handler(admin_msg, IsAdminFilter(), text=Buttons.admin.cancel, state='*')
    dp.register_message_handler(admin_msg, IsAdminFilter(), text=Buttons.menu.admin, state='*')
    dp.register_message_handler(admin_statistic, text=Buttons.admin.statistic, state='*')


def plot_data(data: list[TimedBaseModel], name: str, color: str, alpha: int, ax: Axes, fig):
    objects = [obj.created_at.strftime('%d.%m.%Y') for obj in data]
    dates = [obj.created_at for obj in data]
    dates.sort()
    days = (now() - now().replace(day=dates[0].day, month=dates[0].month, year=dates[0].year)).days + 1
    dates = [(dates[0] + timedelta(days=i)).strftime('%d.%m.%Y') for i in range(days)]
    counts = [objects.count(date) for date in dates]
    ax.plot(dates, counts, label=name, color=color)
    ax.scatter(dates, counts, color=color)
    ax.fill_between(dates, counts, alpha=alpha/10, color=color)
    ax.legend()
    fig.autofmt_xdate()
    ax.set_xlabel('Дата реєстрації')
    ax.set_ylabel('Кількість')
    ax.set_title('Статистика росту аудиторії')
    ax.grid(ls='--')
    ax.minorticks_on()
    return ax