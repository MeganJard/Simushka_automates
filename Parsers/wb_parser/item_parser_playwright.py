import re
from datetime import datetime
import pandas as pd
from playwright.sync_api import sync_playwright
from googlesearch import search
from random import choice
import xml.etree.ElementTree as ET


PLOSHADKA = 'wildberries.ru'
proxies = ["http://21585V:zjKmJR@5.8.83.151:8000",
           'http://3CNEf9:HVH50t@46.8.59.108:8000',
           'http://3CNEf9:HVH50t@46.8.58.6:8000',
           'http://3CNEf9:HVH50t@46.8.58.251:8000',
           'http://3CNEf9:HVH50t@46.8.58.68:8000',
           'http://3CNEf9:HVH50t@46.8.59.223:8000'
]
def yandex_search(query, platform):
    while True:
        try:
        # Выполняем поиск в Google
            search_results = list(search(query, proxy=choice(proxies)))  # num — количество результатов, pause — задержка между запросами
            print(search_results)
            # Фильтруем результаты по платформе и пути /product/
            answer = []
            for link in search_results:
                if platform in link and '/catalog/' in link and link.split('/')[4].isdigit():
                    answer.append(link.replace('global.', ''))
            
            # Возвращаем первые 5 уникальных ссылок
            return list(set(answer))
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return None

def initiate_dict(page_dict):
    keys = [
        'Артикул площадки', 'Бренд', 'Есть в наличии', 'Название товара на площадке',
        'Объем', 'Площадка', 'Ссылка на товар', 'Цена', 'Цена со скидкой',
        'Название товара наше', 'Дата парсинга'
    ]
    for key in keys:
        page_dict[key] = []
    return page_dict

def add_new_element(page_dict, brand, article, title, volume_1, item_block_href, price, vnal, our_name):
    page_dict['Площадка'].append(PLOSHADKA)
    page_dict['Бренд'].append(brand)
    page_dict['Артикул площадки'].append(article)
    page_dict['Название товара на площадке'].append(title)
    page_dict['Объем'].append(volume_1)
    page_dict['Ссылка на товар'].append(item_block_href)
    page_dict['Цена'].append(price[1])
    page_dict['Цена со скидкой'].append(price[0])
    page_dict['Есть в наличии'].append(True)
    page_dict['Дата парсинга'].append(str(datetime.today().strftime("%Y-%m-%d")))
    page_dict['Название товара наше'].append(our_name)

def get_brand_name(page):
    try:
        page.wait_for_selector('xpath=/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[9]/div[1]/a', timeout=5000) #Ожидание для загрузки страницы
        return page.query_selector('xpath=/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[9]/div[1]/a').inner_text()
    except Exception as e:
        print("No brand name found")
        return ''

def get_article(url):
    try:
        return url.split('/')[4]
    except Exception as e:
        print('No article found')
        return ''

def get_volume(page):
    try:
        return page.query_selector('.product-params__table').inner_text()
    except Exception as e:
        return ''

def get_price(page):
    prices = page.query_selector('xpath=/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[14]/div/div[1]/div[1]/div').inner_text()
    prices = prices.replace('с WB Кошельком', '').replace('\n', '').replace('\u2009', '').replace('\xa0', '').split('₽')
    prices = list(int(i) for i in prices if i != '')
    return sorted(prices)[:2]

def get_product_name(page):
    return page.query_selector('.product-page__title').inner_text()

def xml_unpack(operation_id):
    tree = ET.parse(fr'C:\Users\admin\PycharmProjects\pythonProject\price_parsers\analysis\search_results\{operation_id}.xml')
    root = tree.getroot()

    # Список для хранения значений из тегов <url>
    urls = []

    # Ищем все теги <url> в XML
    for url_tag in root.iter('url'):
        # Добавляем текст внутри тега <url> в список
        urls.append(url_tag.text)

    return urls

def parse(item, operation_id):
    with sync_playwright() as p:
        urls = xml_unpack(operation_id)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(viewport={'width': 1800, 'height': 900})
        page = context.new_page()


        next_line = '\n'
        print(f'Паршу {item} по ссылкам {next_line.join(urls)}')
        if not urls:
            return
        page_dict = {}
        initiate_dict(page_dict)

        for url in urls:
            try:
                page.goto(url)
                brand_name = get_brand_name(page)
                product_name = get_product_name(page)
                artikul = get_article(url)
                price = get_price(page)
                volume = get_volume(page)
                add_new_element(page_dict, brand_name, artikul, product_name, volume, url, price, True, item)
            except Exception as e:
                continue

        browser.close()

        invalid_chars = r'[\/:*?"<>|]'
        try:
            if len(page_dict['Цена']) > 0:
                pd.DataFrame(page_dict).to_excel(
                 fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\{PLOSHADKA}_{re.sub(invalid_chars, '_', item)}.xlsx")
        except Exception as e:
            print(f"Error saving file: {e}")

if __name__ == '__main__':
    print(yandex_search(f'wildberries.ru/catalog  Koleston Perfect Me+ Краска для волос 8/1 Песчаная буря', PLOSHADKA))