import re
from datetime import datetime
import pandas as pd
from playwright.sync_api import sync_playwright
from googlesearch import search
from random import choice
import xml.etree.ElementTree as ET


PLOSHADKA = 'goldapple.ru'
proxies = ["http://21585V:zjKmJR@5.8.83.151:8000",
           'http://3CNEf9:HVH50t@46.8.59.108:8000',
           'http://3CNEf9:HVH50t@46.8.58.6:8000',
           'http://3CNEf9:HVH50t@46.8.58.251:8000',
           'http://3CNEf9:HVH50t@46.8.58.68:8000',
           'http://3CNEf9:HVH50t@46.8.59.223:8000',
           'http://HLdTGM:p1XsTz@45.132.22.186:8000',
           'http://yKSxArtBWC:UllLzPFQkS@185.236.21.105:11223'
]
def yandex_search(query, platform):
    while True:
        try:
        # Выполняем поиск в Google
            search_results = list(search(query, proxy=proxies[4]))  # num — количество результатов, pause — задержка между запросами
            print(search_results)
            # Фильтруем результаты по платформе и пути /product/
            answer = []


            for link in search_results:
                is_valid_url = False
                try:
                    is_valid_url = link.split('/')[3].split('-')[0].isdigit()
                except:
                    pass
                if platform in link and len(link.split('/')) == 4 and is_valid_url:
                    answer.append(link)
            
            # Возвращаем первые 5 уникальных ссылок
            return answer[:1]
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            return None
        

def initiate_dict(page_dict):
    keys = ['Артикул площадки', 'Бренд', 'Есть в наличии', 'Название товара на площадке', 'Объем', 'Площадка', 'Ссылка на товар', 'Цена', 'Цена со скидкой', 'Название товара наше', 'Дата парсинга']
    for key in keys:
        page_dict[key] = []
    return page_dict

def add_new_element(page_dict, brand, article, title, volume_1, item_block_href, price, vnal, our_name):
    price = [i.replace('₽', '').replace(' ', '') if i else '' for i in price]
    price = [int(p) if p.isdigit() else p for p in price]
    price.sort(reverse=True)

    page_dict['Площадка'].append(PLOSHADKA)
    page_dict['Бренд'].append(brand)
    page_dict['Артикул площадки'].append(article)
    page_dict['Название товара на площадке'].append(title)
    page_dict['Объем'].append(volume_1)
    page_dict['Ссылка на товар'].append(item_block_href)
    page_dict['Цена'].append(price[0])
    page_dict['Цена со скидкой'].append(price[1])
    page_dict['Есть в наличии'].append(vnal)
    page_dict['Дата парсинга'].append(str(datetime.today().strftime("%Y-%m-%d")))
    page_dict['Название товара наше'].append(our_name)

def parse_product(page, page_dict, item_block_href, our_name):

    page.goto(item_block_href)
    page.wait_for_timeout(6000)
    page.evaluate("document.body.style.zoom='25%'")
    page.wait_for_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/div/div/h1/span', timeout=3000)
    title = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/div/div/h1/span').text_content()
    brand = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/div/div/h1/a').text_content()
    article = ''
    price = get_price(page)
    volume = get_volume(page)
    vnal = get_vnal(page)
    add_new_element(page_dict, brand, article, title, volume, item_block_href, price, vnal, our_name)

def get_price(page):
    try:
        usual_price = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[1]/div[1]').text_content()
        offer_price = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[2]/div[1]').text_content()
    except Exception:
        try:
            usual_price = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[1]/div').text_content()
            offer_price = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[2]/div[1]').text_content()
        except Exception:
            usual_price = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div').text_content()
            offer_price = None
    return [usual_price, offer_price]

def get_vnal(page):
    return page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[3]/div[1]').text_content() != 'нет в наличии'

def get_volume(page):
    try:
        volume = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[1]/div[1]').text_content()
    except Exception:
        volume = ''
    try:
        color = page.query_selector('//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[1]/div[2]/div[1]/div/span/div').text_content()
    except Exception:
        color = ''
    return volume + '\n' + color

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
        urls = xml_unpack(operation_id)[:1]
        invalid_chars = r'[\/:*?"<>|]'+"'"
        if urls == [] or urls is None:
            return
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()


        page_dict = {}
        initiate_dict(page_dict)
        print(f'Работа с позицией {item}')
        print(urls)
        page.goto('https://goldapple.ru')
        page.wait_for_timeout(3000)
        for url in urls:
            try:
                parse_product(page, page_dict, url, item)
            except Exception as e:
                browser.close()
                return
        browser.close()
        
        invalid_chars = r'[\/:*?"<>|]'
        try:
            pd.DataFrame(page_dict).to_excel(fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\{PLOSHADKA}_{re.sub(invalid_chars, '_', item)}.xlsx")
        except:
            pass

if __name__ == '__main__':
    parse("Крем ORJENA для глаз с витаминами")