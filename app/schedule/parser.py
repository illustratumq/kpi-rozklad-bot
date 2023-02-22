import requests
from pprint import pprint


class Lecture:

    def __init__(self, data: dict):
        self.id = data.get('lecturerId')
        self.name = data.get('name')
        self.place = data.get('place')
        self.tag = data.get('tag')
        self.teacherName = data.get('teacherName')
        self.time = data.get('time')
        self.type = data.get('type')


class Day:

    def __init__(self, data: dict):
        self.day = data.get('day')
        self.pairs = self._lectures(data.get('pairs'))

    @staticmethod
    def _lectures(data: list[dict]) -> list[Lecture]:
        lectures_ = []
        for lecture in data:
            lectures_.append(Lecture(lecture))
        return lectures_


class Week:

    def __init__(self, data: list[dict]):
        self.days = self._days(data)

    @staticmethod
    def _days(data: list[dict]) -> list[Day]:
        days_ = []
        for day in data:
            days_.append(Day(day))
        return days_


class Group:

    def __init__(self, data: dict):
        self.name = data.get('name')
        self.id = data.get('id')
        self.faculty = data.get('faculty')
        self.schedule = self.schedule()
        self.first_week = Week(self.schedule.get('data').get('scheduleFirstWeek'))
        self.second_week = Week(self.schedule.get('data').get('scheduleSecondWeek'))

    def schedule(self):
        url = f'https://schedule.kpi.ua/api/schedule/lessons?groupId={self.id}'
        return requests.get(url).json()

    def lectures(self):
        lectures = []
        for day in self.first_week.days + self.second_week.days:
            for pair in day.pairs:
                lecture = dict(name=pair.name, tag=pair.tag)
                if lecture not in lectures:
                    lectures.append(lecture)
        return lectures


class ScheduleController:

    def __init__(self):
        self.groups = self.group_list()

    @staticmethod
    def group_list() -> list[dict]:
        # get all group list
        groups_list = []
        groups = requests.get('https://schedule.kpi.ua/api/schedule/groups').json().get('data')
        for group in groups:
            groups_list.append(group)
        return groups_list

    def get_group(self, name: str):
        for group in self.groups:
            if group.get('name') == name:
                return Group(group)


# group = ScheduleController().get_group('ДП-92')
# pprint(group.lectures())