import requests
from bs4 import BeautifulSoup as bs
from typing import NamedTuple, List, Optional
from datetime import datetime, date
import logging


class LessonContent(NamedTuple):
    lesson_time_start: str  # datetime
    lesson_type: str
    lesson_pair_number: int
    lesson_name: str
    lecturer_surname: str
    lesson_place: Optional[str]
    lesson_link: Optional[str]
    lesson_group: str


class DayContent(NamedTuple):
    lessons_day: datetime
    lessons_list: List[LessonContent]


def fetch_schedule(week):
    url = f"https://schedule.kantiana.ru/{week}"
    data = {
        "group_last": "03_ПМИ_23_о_ИП_1",
        "group": None,
        "setdate": date.today().strftime("%Y-%m-%d"),  # "2023-09-08"
    }
    response = requests.post(url, data)
    return response


def parse_schedule(data: requests.Response) -> List[DayContent]:
    soup = bs(data.text, "lxml")
    try:
        pars_res_list = soup.find_all(class_="accordion-item")
        week_data: list = []
        for i in pars_res_list:  # iteration by days
            day_lectures = []
            # print('******** day ******')
            for ii in i.find_all(class_="card"):  # iteration by lessons
                # print('*****  lesson *******')
                lesson_row_list = [
                    i.text.strip() for i in ii.find_all(class_="card-text text-center")
                ]
                # print(f"{lesson_row_list=}")
                lesson_row_list_time = (
                    ii.find(class_="col-sm-3 btn-primary rounded-3 align-middle")
                    .text.strip()
                    .split()
                )
                # print(f"{lesson_row_list_time=}")
                # pp(ii)
                # print(f'{i.find(class_="col-sm-3 btn-primary rounded-3 align-middle").text.strip().split()}')
                # print(lesson_row_list_time)
                # print(f"{lesson_row_list    }")
                lesson = LessonContent(
                    # lesson_time_start=datetime.strptime(i.find(class_="accordion-button").text.strip().split()[0], "%d.%m.%Y"),
                    lesson_time_start=lesson_row_list_time[2],
                    lesson_name=lesson_row_list[0],
                    # lesson_pair_number= lesson_row_list_time[0],
                    lesson_pair_number=lesson_row_list_time[0],
                    lecturer_surname=lesson_row_list[1].split()[0],
                    lesson_group=lesson_row_list[-1],
                    lesson_type=ii.find(
                        class_="card-text rounded-3 text-center"
                    ).text.strip(),
                    lesson_link=next(
                        iter([i["href"] for i in ii.find_all("a", href=True)]), None
                    ),
                    lesson_place=lesson_row_list[2],
                )
                day_lectures.append(lesson)
            day_shedule = DayContent(
                lessons_day=datetime.strptime(
                    i.find(class_="accordion-button").text.strip().split()[0],
                    "%d.%m.%Y",
                ),
                lessons_list=day_lectures,
            )
            week_data.append(day_shedule)
        return week_data
    except BaseException as BE:
        print(f"{str(BE)}")


def row_schedule_on_week(action):
    return parse_schedule(fetch_schedule(action))


def get_prepared_schedule_data():
    """
    getting schedule for one week - if now if middle - getting next full week"""
    days: list = row_schedule_on_week("week")
    if date.today().weekday() == 0:  # monday
        pass
    else:
        days.extend(row_schedule_on_week("nextweek"))

    return days


def shorter_str(
    s: str, one_strip: int = 6, max_splits: int = 2, multiple_strip: int = 3
):
    if " " in s:
        return " ".join([i[:multiple_strip] for i in s.split()[:max_splits]])
    else:
        return s[:one_strip]


def generate_row(row_list: list):
    return "\t".join([i for i in row_list])


def get_table_with_shedule():
    """i know about tabulate and tables, but wont use mine solution"""
    logging.info("some")
    schedule_weeeks: List[DayContent] = get_prepared_schedule_data()

    print("+++++++++++++++++++++++++")
    if True:
        for i in schedule_weeeks:
            if i:
                print(i.lessons_day)
                for ii in i.lessons_list:
                    # pp(ii)
                    # print("-"*10)
                    print(
                        generate_row(
                            [
                                ii.lesson_time_start,
                                ii.lesson_pair_number,
                                shorter_str(ii.lesson_name),
                                shorter_str(ii.lesson_type, one_strip=4, max_splits=1),
                                shorter_str(ii.lecturer_surname, one_strip=5),
                                ii.lesson_place.split()[0]
                                if ii.lesson_place
                                else "    ",
                                ii.lesson_link if ii.lesson_link else "    ",
                                shorter_str(
                                    ii.lesson_group,
                                    max_splits=2,
                                    one_strip=3,
                                    multiple_strip=3,
                                ),
                            ]
                        )
                    )
                print("*" * 10)
            pass
    return None


# get_prepared_schedule_data()
print(get_table_with_shedule())
