import requests
from bs4 import BeautifulSoup as bs
from typing import NamedTuple, List, Optional
from datetime import datetime, date


class LessonContent(NamedTuple):
    lesson_time_start: datetime
    lesson_type: str
    lesson_name: str
    lecturer_surname: str
    lesson_place:Optional[str]
    lesson_link: Optional[str]
    lesson_group: str
class DayContent(NamedTuple):
    lessons_day: datetime
    lessons_list:List[LessonContent]

action = "week"
action = "nextweek"
def fetch_schedule_data(week):

    url = f"https://schedule.kantiana.ru/{action}"
    data = {
        "group_last": "03_ПМИ_23_о_ИП_1",
        "group": None,
        "setdate": "2023-09-08"
    }
    response = requests.post(
        url, data
    )
    return response


def parse_data(data:requests.Response):
#  ->List[DayContent]:
    soup = bs(
        data.text,
        "lxml"
    )
    pars_res_list = soup.find_all(
        class_="accordion-item"
        )
    week_data:list = []
    for i in pars_res_list: # iteration by days
        day_lectures = []
        for ii in i.find_all(class_="card"): # iteration by lessons
            lesson_row_list = [i.text.strip() for i in ii.find_all(class_="card-text text-center")]
            lesson = LessonContent(
                lesson_time_start=datetime.strptime(i.find(class_="accordion-button").text.strip().split()[0], "%d.%m.%Y"),
                lesson_name = lesson_row_list[0],
                lecturer_surname = lesson_row_list[1].split()[0],
                lesson_group = lesson_row_list[-1],
                lesson_type=ii.find(class_="card-text rounded-3 text-center").text.strip(),
                lesson_link=next(iter([i["href"] for i in ii.find_all("a", href=True)]), None),
                lesson_place=lesson_row_list[2]
            )
            day_lectures.append(lesson)
        day_shedule = DayContent(
            lessons_day=datetime.strptime(i.find(class_="accordion-button").text.strip().split()[0], "%d.%m.%Y"),
            lessons_list=day_lectures
        )
        week_data.append(day_shedule)
    return week_data

def get_schedule_on_week(action):
    return parse_data(fetch_schedule_data(action))

def get_prepared_schedule_data():
    """
    getting schedule for one week - if now if middle - getting next full week"""
    days:list = get_schedule_on_week("week")
    if  date.today().weekday() == 0: # monday
        pass
    else:
        days = days.append(get_schedule_on_week("nextweek"))
    # print(days)
    return days


def get_table_with_shedule(data):
    """i know about tabulate and tables, but wont use mine solution"""
    # for i in data:
    pass


get_prepared_schedule_data()