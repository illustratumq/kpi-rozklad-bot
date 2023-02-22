import json
from datetime import datetime

import pytz
from babel.dates import format_date

from app.config import Config


def now():
    config = Config.from_env()
    return datetime.now().replace(microsecond=0).astimezone(pytz.timezone(config.misc.timezone))


def localize(date: datetime):
    config = Config.from_env()
    return date.replace(microsecond=0).astimezone(pytz.timezone(config.misc.timezone))


class Timer:

    def __init__(self, data: dict):
        self.week = data['week']
        self.day = data['day']
        self.lesson = data['lesson']
        self.second_week = data['second_week']
        self.pairbreak = data['pairbreak']


class Current:

    def __init__(self, path: str):
        self.path = path

    @property
    def lesson(self):
        date = now()
        pair_1 = date.replace(hour=8, minute=30)
        pair_2 = date.replace(hour=10, minute=25)
        pair_3 = date.replace(hour=12, minute=20)
        pair_4 = date.replace(hour=14, minute=15)
        pair_5 = date.replace(hour=16, minute=10)
        pair_6 = date.replace(hour=18, minute=5)
        if date > pair_6 or date < pair_1:
            return 0
        elif pair_1 <= date < pair_2:
            return 1
        elif pair_2 <= date < pair_3:
            return 2
        elif pair_3 <= date < pair_4:
            return 3
        elif pair_4 <= date < pair_5:
            return 4
        elif pair_5 <= date < pair_6:
            return 5

    @property
    def pairbreak(self):
        date = now()
        break_1 = date.replace(hour=10, minute=5)
        pair_2 = date.replace(hour=10, minute=25)
        break_2 = date.replace(hour=12, minute=0)
        pair_3 = date.replace(hour=12, minute=20)
        break_3 = date.replace(hour=13, minute=55)
        pair_4 = date.replace(hour=14, minute=15)
        break_4 = date.replace(hour=15, minute=50)
        pair_5 = date.replace(hour=16, minute=10)
        return any(
            [
                break_1 <= date < pair_2,
                break_2 <= date < pair_3,
                break_3 <= date < pair_4,
                break_4 <= date < pair_5
            ]
        )

    @property
    def day(self):
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
        day = format_date(now(), locale='uk_UA', format='EEE').capitalize()
        if day == 'Нд':
            return 0
        return days.index(day)

    @property
    def week(self):
        with open(self.path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return int(data['current_week'])

    def current(self):
        return Timer(dict(lesson=self.lesson, day=self.day, week=self.week,
                          second_week=1 if self.week == 2 else 2, pairbreak=self.pairbreak))


