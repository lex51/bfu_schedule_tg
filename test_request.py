from requests import post
from bs4 import BeautifulSoup as bs



from pprint import pprint as pp


print("\n"*10)

url = "https://schedule.kantiana.ru/nextweek"
data = {
    "group_last": "03_ПМИ_23_о_ИП_1",
    "group": None,
    "setdate": "2023-09-08"
}
response = post(
    url, data
)
soup = bs(
    response.text,
    # 'html.parser'
    "lxml"
)
# pars_res = soup.find_all(
#     class_="card-body"
#     # class_=
# )
pars_res_list = soup.find_all(
    # class_="card-body"
    class_="accordion-body"
    )
# pp(
#     # len(pars_res_list)
#     pars_res_list[2]
# )

for i in pars_res_list[2:3]: # by days
    pp(i)
    for ii in i.find_all(class_="card-body"): # by lessons
        # pp(ii)
        pass
    print("\n")
    print("*"*8)