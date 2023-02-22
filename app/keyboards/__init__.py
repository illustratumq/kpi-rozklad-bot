from dataclasses import dataclass


@dataclass
class Admin:
    statistic: str = 'Переглянути статистику 📊'
    create_message: str = 'Розсилка ✉'
    cancel: str = 'Відмінити ⤵'
    send: str = 'Надіслати повідомлення 📨'
    skip: str = 'Пропустити ➡'
    edit: str = 'Редагувати ✂'
    news: str = 'Інформація 📬'


@dataclass
class Menu:
    today: str = 'Розклад на сьогодні 📚'
    next_day: str = 'Розклад на завтра 📚'
    current_week: str = 'Цей тиждень 🔽'
    next_week: str = 'Наступний 🔼'
    my_group: str = 'Моя група 🎓'
    settings: str = 'Налаштування ⚙'
    about_bot: str = 'Про бота ℹ'
    back: str = '◀ В головне меню'
    search_group: str = '🔍 Шукати групу'
    admin: str = 'В адмін панель 🗝'
    news: str = 'Повідомлення 📬'


@dataclass
class Settings:
    notify_on: str = 'Сповіщення: включити'
    notify_off: str = 'Сповіщення: виключити'
    mark_on: str = 'Відмічати в чаті: дозволити'
    mark_off: str = 'Відмічати в чаті: заборонити'


@dataclass
class Group:
    change: str = 'Змінити групу 🔄'
    info: str = 'Про груповий чат 🔖'
    add_chat: str = 'Додати чат 💬'
    del_chat: str = 'Видалити чат 🗯'
    back = Menu.back


@dataclass
class Today:
    info: str = 'Про сповіщення та посилання 🔖'
    back = Menu.back


class Buttons:
    menu = Menu()
    today = Today()
    group = Group()
    settings = Settings()
    admin = Admin()