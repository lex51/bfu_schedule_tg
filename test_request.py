import requests
from bs4 import BeautifulSoup as bs
from typing import NamedTuple, List, Optional
from datetime import datetime, date
import re
import json

class LessonContent(NamedTuple):
    lesson_time_start: str  # datetime
    lesson_type: str
    lesson_pair_number: int
    lesson_name: str
    lecturer_surname: str
    lesson_place: Optional[str] = None
    lesson_link: Optional[str] = None
    lesson_group: Optional[str] = None
    lesson_corpus: Optional[int] = None
    lesson_street: Optional[str] = None
    lesson_cabinet: Optional[str] = None


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
                lesson_place=lesson_row_list[2]
                # print(f"{lesson_row_list=}")
                lesson_row_list_time = (
                    ii.find(class_="col-sm-3 btn-primary rounded-3 align-middle")
                    .text.strip()
                    .split()
                )

                lesson = LessonContent(
                    lesson_time_start=lesson_row_list_time[2],
                    lesson_name=lesson_row_list[0],
                    lesson_pair_number=lesson_row_list_time[0],
                    lecturer_surname=lesson_row_list[1].split()[0],
                    lesson_group=lesson_row_list[-1],
                    lesson_type=ii.find(
                        class_="card-text rounded-3 text-center"
                    ).text.strip(),
                    lesson_link=next(
                        iter([i["href"] for i in ii.find_all("a", href=True)]), None
                    ),
                    lesson_corpus=re.search(r'корпус \d{,3}', lesson_place).group().split()[-1] if lesson_place else None,
                    lesson_street=re.search(r'ул.(.*?), д.', lesson_place).group(1) if lesson_place else None,# ул.([\S+. -]+),
                    lesson_cabinet=re.search(r'ауд_\d_(.*?) \(', lesson_place).group(1) if lesson_place else None,
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
    getting schedule for one week - if now
    if in middle - getting next full week
    and filter days
    """
    days: List[DayContent] = row_schedule_on_week("week")
    current_day = date.today()
    if current_day.weekday() == 0:  # monday
        pass
    else:
        days.extend(row_schedule_on_week("nextweek"))
    
    return filter(
        lambda d : d.lessons_day.date() >= current_day, days
    )


def shorter_str(
    s: str, one_strip: int = 6, max_splits: int = 2, multiple_strip: int = 3, join:bool=False, 
):
    if " " in s and not join:
        return " ".join([i[:multiple_strip] for i in s.split()[:max_splits]])
    elif join:
        return "".join(i for i in s.split())[:multiple_strip]
    else:
        return s[:one_strip]
    

def shorter_street(
        s: str, single_slice:int=3
):
    if s:
        if " " in s:
            return s.split()[-1][:single_slice]
        elif "." in s:
            return s.split(".")[-1][:single_slice]
    return ""


def generate_row(row_list: list):
    return "\t".join([i if i else "  "  for i in row_list])

def find_week_day(i:int):
    return ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс'][i]

def prepare_markdown_link(s:str):
    return f"```[link]({s})```"
    # return f'</code><a href="{s}">!!!_link_!!!</a><code>'
    # return f'</pre><a class="inline" href="{s}">!!!_link_!!!</a><pre class="inline">'



def get_table_with_shedule():
    """i know about tabulate and tables, but wont use mine solution"""
    schedule_weeeks: List[DayContent] = get_prepared_schedule_data()
    formatted_rows_list = []
    if True:
        for i in schedule_weeeks:
            if i:
                # print(i.lessons_day)
                lesson_day = i.lessons_day
                formatted_day_line = f"-- {lesson_day.date()} - {find_week_day(lesson_day.weekday())} --"
                formatted_rows_list.append(
                    formatted_day_line
                    )
                for ii in i.lessons_list:
                    lect_place = '      '
                    if ii.lesson_link:
                        if ii.lesson_link == 'webinar':
                            lect_place = "~ready"
                        else:
                            lect_place = prepare_markdown_link(ii.lesson_link)
                    elif ii.lesson_street:
                        lect_place = ' '.join([
                            shorter_street(ii.lesson_street), 'k'+ii.lesson_corpus
                        ])

                    formatted_rows_list.append(
                        generate_row(
                            [
                                ii.lesson_time_start,
                                ii.lesson_pair_number,
                                shorter_str(ii.lesson_name),
                                shorter_str(ii.lesson_type, one_strip=4, max_splits=1),
                                shorter_str(ii.lecturer_surname, one_strip=5),
                                lect_place,
                                shorter_str(
                                    ii.lesson_group,
                                    max_splits=2,
                                    one_strip=3,
                                    multiple_strip=2,
                                    join=True,
                                ),
                            ]
                        )
                    )
    return formatted_rows_list


class Conf:
    pass

def create_and_prepare_msg():
    l = get_table_with_shedule()
    msg = '\n'.join(l)
    msg = f'```{msg}```'
    return msg

def send_tg_msg(l:list):
    msg = '\n'.join(l)
    msg = f'```{msg}```'
    # msg = f'<pre class="inline">\n{msg}\n</pre>'
    # msg = f"<code>\n{msg}\n</code>"
    # msg = f"<pre><code>\n{msg}\n</code></pre>"

    # print(msg)
    url = f"https://api.telegram.org/bot{Conf.tg_token}/sendMessage?chat_id={Conf.tg_chat}&text={msg}&disable_notification=true&parse_mode=html"
    url = f"https://api.telegram.org/bot{Conf.tg_token}/sendMessage?chat_id={Conf.tg_chat}&text={msg}&disable_notification=true&parse_mode=markdown"

    # print(url)
    tg_response = requests.get(url).json()
    print(tg_response)

# get_prepared_schedule_data()
# print(get_table_with_shedule())
# send_tg_msg(
#     get_table_with_shedule()
# )


def handler(event, context):
    body = json.loads(event['body'])
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'method': 'sendMessage',
            'chat_id': body['message']['chat']['id'],
            'text':  create_and_prepare_msg(),
            'parse_mode': 'markdown'
        }),
        'isBase64Encoded': False
    }