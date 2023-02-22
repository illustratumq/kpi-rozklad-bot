import json
from datetime import timedelta

import requests
from aiogram import Bot
from apscheduler_di import ContextSchedulerDecorator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.schedule.decorator import ScheduleDecorator
from app.schedule.timer import Current, now
from database.services.repos import UserRepo, LectureRepo, GroupRepo, NotifyRepo

DAYS = ['Пн', 'Вв', 'Ср', 'Чт', 'Пт', 'Сб']


def date(seconds: int = 5):
    return dict(trigger='date', next_run_time=now() + timedelta(seconds=seconds), misfire_grace_time=300)


def cron(hour: int, minute: int | str):
    return dict(trigger='cron', day='*', minute=minute, hour=hour, max_instances=2, misfire_grace_time=300)


async def setup_executors(scheduler:  ContextSchedulerDecorator):
    scheduler.add_job(lecture_sender, **cron(8, 25))
    scheduler.add_job(lecture_sender, **cron(10, 20))
    scheduler.add_job(lecture_sender, **cron(12, 15))
    scheduler.add_job(lecture_sender, **cron(14, 10))
    scheduler.add_job(lecture_sender, **cron(16, 5))
    scheduler.add_job(week, trigger='cron', day_of_week='sun', hour=23, minute=59, second=59)
    scheduler.add_job(week_checker, trigger='date', next_run_time=now() + timedelta(seconds=5),
                      misfire_grace_time=300)


async def week_checker():
    path = 'app/schedule/week.json'
    try:
        response = requests.get('https://schedule.kpi.ua/api/time/current').json()
        week_number = int(response['data']['currentWeek'])
        data = dict(current_week=int(week_number)+1)
        with open(path, mode='w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except requests.exceptions.ConnectionError:
        pass


async def lecture_sender(session: sessionmaker, bot: Bot, timer: Current):
    session: AsyncSession = session()
    user_db = UserRepo(session)
    group_db = GroupRepo(session)
    lecture_db = LectureRepo(session)
    notify_db = NotifyRepo(session)
    current = timer.current()
    groups = await user_db.get_using_groups()
    hour = int(now().strftime('%H'))
    for group_id in groups:
        group = await group_db.get_group(group_id)
        decorator = ScheduleDecorator(group.schedule)
        day = decorator.group.day(DAYS[current.day], current.week)
        for pair in decorator.group.lectures(day):
            lecture = await lecture_db.get_lecture(group_id=group.group_id, name=pair['name'], tag=pair['tag'])
            if int(pair['time'].split('.')[0]) == hour:
                marker = decorator.get_marker(lecture.tag)
                url = f'\n🔗{lecture.url}' if lecture.url else ''
                text = (
                    f'{pair["time"]} - Пара почнеться за декілька хвилин...\n\n'
                    f'<b>{marker} {lecture.name}\n</b>{url}\n\n'
                    f'@kpi_rozklad_bot'
                )
                try:
                    await bot.send_message(group.chat_id, text)
                except:
                    await group_db.update_group(group.group_id, chat_id=None)
                notifies = await notify_db.get_notifies_by_lecture(lecture.lecture_id)
                for notify in notifies:
                    if notify.notification:
                        user = await user_db.get_user(notify.user_id)
                        if user.notification and user.group_id == group_id:
                            try:
                                await bot.send_message(notify.user_id, text)
                            except:
                                pass
    await session.commit()
    await session.close()


async def week():
    path = 'app/schedule/week.json'
    with open(path, mode='r', encoding='utf-8') as file:
        data = json.load(file)
    current_week = data['current_week']
    change_week = 1 if current_week == 2 else 2
    data.update(current_week=change_week)
    with open(path, mode='w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)
