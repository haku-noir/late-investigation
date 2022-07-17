from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By

from .models import Route

CHROMEDRIVER = '/opt/chrome/chromedriver'
URL = 'https://traininfo.jreast.co.jp/delay_certificate/'

def getinfos():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    chrome_service = fs.Service(executable_path=CHROMEDRIVER) 
    driver = webdriver.Chrome(service=chrome_service, options=options)
    driver.get(URL)
    html = driver.page_source

    names = []
    tags = driver.find_elements(by=By.CSS_SELECTOR, value="th.fontBold")
    for tag in tags:
        names.append(tag.text.replace('\n', ' ').replace('・', ''))

    times = []
    tags = driver.find_elements(by=By.CSS_SELECTOR, value="td.w14p")
    for tag in tags:
        times.append(tag.text.replace('掲載なし', 'なし').replace('掲載準備中', '未確定'))
    times = times[1::5]

    info ={}
    for name, time in zip(names, times):
        info[name] = time

    routes = Route.objects.all()
    times = [info.get(route.name) if route.name in info else "不明" for route in routes]
    route_infos = []
    for i in range(len(routes)):
        route_infos.append({'route':routes[i], 'time':times[i]})

    return route_infos
