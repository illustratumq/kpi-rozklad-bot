import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.schedule.parser import ScheduleController
from database.services.repos import GroupRepo, LectureRepo

log = logging.getLogger(__name__)


async def setup_groups(group_db: GroupRepo, lecture_db: LectureRepo):
    scheduler = ScheduleController()
    log.info(f'Нараховано {len(scheduler.groups)} груп')
    c = 0
    for group in scheduler.group_list():
        try:
            group = scheduler.get_group(group['name'])
            group_id = group.id
            name = group.name
            faculty = group.faculty
            group.schedule.update(name=name, faculty=faculty, group_id=group_id)
            schedule = group.schedule
            if await group_db.get_group(group_id) is None:
                await group_db.add(group_id=group_id, name=name, faculty=faculty, schedule=schedule)
            for lecture in group.lectures():
                await lecture_db.add(group_id=group_id, **lecture)
            c += 1
            if c % 100 == 0:
                log.info(f'Збережено {c} груп')
        except Exception as Error:
            log.error(f'Помилка {Error}')
    log.info('Групи додано в базу даних')


async def one_setup(session: sessionmaker):
    session: AsyncSession = session()
    group_db = GroupRepo(session)
    lecture_db = LectureRepo(session)
    await setup_groups(group_db, lecture_db)
    await session.commit()
    await session.close()
