from requests import post
from bs4 import BeautifulSoup as bs



# from pprint import pprint as pp


print("\n"*10)
action = "week"
action = "nextweek"
url = f"https://schedule.kantiana.ru/{action}"
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
pars_res_list = soup.find_all(
    class_="accordion-item"
    )


for i in pars_res_list:
    # print(i) # date, next block with id="accordion-header"
    print(i.find(class_="accordion-button").text.strip())
    
    for ii in i.find_all(class_="card"):
        # print(ii)
        # interesting json in class="btn btn-success teacherCL"
        print(f'time - {ii.find(class_="col-sm-3 btn-primary rounded-3 align-middle").text.strip()}')
        print(f'type - {ii.find(class_="card-text rounded-3 text-center").text.strip()}')
        print(f'list - {[i.text.strip() for i in ii.find_all(class_="card-text text-center")]}')
        print(f'link - {next(iter([i["href"] for i in ii.find_all("a", href=True)]), None)}')
        # print(f'place - {ii.find(class_="card-text text-center").text.strip()}')
        
        
        print("-"*15)
    
    
    
    print("*"*10)