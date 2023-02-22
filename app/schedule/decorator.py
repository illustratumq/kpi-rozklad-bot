from app.schedule.timer import Current, now


class Lecture:

    def __init__(self, data: dict):
        self.data = data
        self.id = data.get('lecturerId')
        self.name = data.get('name')
        self.place = data.get('place')
        self.tag = data.get('tag')
        self.teacherName = data.get('teacherName')
        self.time = data.get('time')
        self.type = data.get('type')
        self.url = data.get('url')


class Day:

    def __init__(self, data: dict):
        self.name = data.get('day')
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
        self.first_week = Week(data.get('data').get('scheduleFirstWeek'))
        self.second_week = Week(data.get('data').get('scheduleSecondWeek'))

    @staticmethod
    def lectures(day: Day):
        lectures = []
        for pair in day.pairs:
            lecture = dict(name=pair.name, tag=pair.tag, time=pair.time)
            if lecture not in lectures:
                lectures.append(lecture)
        return lectures

    def day(self, day_name: str, week: int):
        days = self.first_week.days if week == 1 else self.second_week.days
        for day in days:
            if day.name.lower() == day_name.lower():
                return day


class ScheduleDecorator:

    timer = Current('app/schedule/week.json')

    def __init__(self, data: dict):
        self.bot_name = '@kpi_rozklad_bot'
        self.schedule = data
        self.group = Group(data)

    def update_url(self, name: str, tag: str, url: str):
        for day in self.group.first_week.days + self.group.second_week.days:
            for lecture in day.pairs:
                if lecture.name == name and lecture.tag == tag:
                    lecture.data.update(url=url)
        return self.schedule

    def delete_url(self, name: str, tag: str):
        for day in self.group.first_week.days + self.group.second_week.days:
            for lecture in day.pairs:
                if lecture.name == name and lecture.tag == tag:
                    lecture.data.update(url=False)
        return self.schedule

    def day(self, day_name: str, week: int, current: bool = False, recompose: bool = False):
        day_number = now().strftime('%d ') if current else ''
        answer = f'<b>📆 {day_number}{day_name}, {week} - тиждень</b>\nГрупа {self.group.name}\n\n'
        days = self.group.first_week.days if week == 1 else self.group.second_week.days
        for day in days:
            if day.name.lower() == day_name.lower():
                if day.pairs:
                    if not recompose:
                        self.decompose_lectures(day)
                    else:
                        self.decompose_lectures(day, tag=False, lec_type=False)
                    self.sort_lectures(day.pairs)
                    for lecture in day.pairs:
                        status = ''
                        tag_start, tag_end = '', ''
                        marker = self.get_marker(lecture.tag, lecture.url)
                        place = f'({lecture.place})' if lecture.place else ''
                        if not recompose:
                            num = self.get_pair_number(lecture.time)
                        else:
                            num = day.pairs.index(lecture) + 1
                        if num == self.timer.lesson and not self.timer.pairbreak and current:
                            status = '🟢 Поточна пара\n'
                            tag_start = '<b>'
                            tag_end = '</b>'
                        elif num == self.timer.lesson + 1 and self.timer.pairbreak and current:
                            status = '⏩ Наступна пара\n'
                        answer += (
                            f'{tag_start}'
                            f'{status}<i>{num} - {lecture.time}</i>\n{lecture.name}\n{lecture.teacherName}'
                            f'\n{marker} {lecture.type} {place}{tag_end}\n\n'
                        )
                else:
                    answer += (
                        'У цей день пар немає 🤟\n\n'
                    )
        return answer + self.bot_name

    @staticmethod
    def get_marker(tag: str, url: bool = False):
        url_marker = '💬' if url else ''
        if tag == 'lec':
            return f'📚{url_marker}'
        elif tag == 'lab':
            return f'🔬{url_marker}'
        else:
            return f'📖{url_marker}'

    @staticmethod
    def get_pair_number(time: str):
        num = int(time.split('.')[0])
        nums = {8: 1, 10: 2, 12: 3, 14: 4, 16: 5, 18: 6}
        return nums.get(num)

    @staticmethod
    def decompose_lectures(day: Day, teacher: bool = True, lec_type: bool = True, tag: bool = True):
        times = [lecture.time for lecture in day.pairs]
        for lecture in day.pairs:
            if times.count(lecture.time) > 1:
                indexes = [i for i in range(len(day.pairs)) if day.pairs[i].time == lecture.time]
                lecture = day.pairs[indexes[0]]
                for i in indexes[1:]:
                    same_lecture = day.pairs[i]
                    if same_lecture.name == lecture.name:
                        delete = False
                        if lecture.teacherName != same_lecture.teacherName and teacher:
                            lecture.teacherName = ', '.join([lecture.teacherName, same_lecture.teacherName])
                            delete = True
                        if lecture.type != same_lecture.type and lec_type:
                            if lecture.url:
                                lecture.type = f'<a href="{lecture.url}">{lecture.type}</a>'
                            elif same_lecture.url:
                                same_lecture.type = f'<a href="{same_lecture.url}">{same_lecture.type}</a>'
                            lecture.type = ', '.join([lecture.type, same_lecture.type])
                            delete = True
                        else:
                            lecture.type = f'<a href="{lecture.url}">{lecture.type}</a>'
                        if lecture.place != same_lecture.place and tag:
                            lecture.place = ', '.join([lecture.place, same_lecture.place])
                            delete = True
                        if delete:
                            del day.pairs[i]
            else:
                if lecture.url:
                    lecture.type = f'<a href="{lecture.url}">{lecture.type}</a>'

    @staticmethod
    def sort_lectures(lectures: list[Lecture]):
        lectures.sort(key=lambda l: int(l.time.split('.')[0]))