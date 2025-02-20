import time
import pandas as pd
from datetime import datetime
import re
from playwright.sync_api import sync_playwright
import xml.etree.ElementTree as ET


PLOSHADKA = 'proficosmetics.ru'

def get_plosh():
    return PLOSHADKA


def initiate_dict(page_dict):
    page_dict['Площадка'] = []
    page_dict['Бренд'] = []
    page_dict['Артикул площадки'] = []
    page_dict['Название товара на площадке'] = []
    page_dict['Объем'] = []
    page_dict['Ссылка на товар'] = []
    page_dict['Цена'] = []
    page_dict['Цена со скидкой'] = []
    page_dict['Есть в наличии'] = []
    page_dict['Дата парсинга'] = []
    page_dict['Кол-во в наличии'] = []
    page_dict['Название товара наше'] = []
    return page_dict

def add_new_element(page_dict, brand, article, title, volume_1, item_block_href, price, vnal, our_name):
    price = list([i.replace('₽', '').replace(' ', '').replace('\u2009', '') if not (i is None) else '' for i in price])
    if price[0].isdigit():
        price[0] = int(price[0])
    if price[1].isdigit():
        price[1] = int(price[1])
    if type(price[0]) == int and type(price[1]) == int:
        price = list(sorted(price, reverse=True))
    if price[0] != int and price[1] == int:
        price[0], price[1] = price[1], price[0]
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
    page_dict['Кол-во в наличии'].append(None)
    page_dict['Название товара наше'].append(our_name)

def get_brand_name(page):
    return page.query_selector('.product_main_desc h4 span').inner_text()

def get_article(page):
    return page.query_selector('.kr_product_info p').inner_text().split(':')[1]

def get_clear_name_and_vol(page):
    product_full_name = page.query_selector('.product_main h1').inner_text()
    if product_full_name.split()[-1] != 'мл' and product_full_name.split()[-1] != 'гр' and product_full_name.split()[-1] != 'г':
        product_clear_name = product_full_name
        volume = None
    else:
        product_clear_name = ' '.join(product_full_name.split()[:-2])
        volume = ' '.join(product_full_name.split()[-2:])
    return product_clear_name, volume

def get_price(page):
    old_price_block = page.query_selector('.old_price-number')
    if old_price_block:
        old_price = old_price_block.inner_text()
    else:
        old_price = ''
    return old_price, ''.join(page.query_selector('.new_price').inner_text().split()[:-1])

def relog(page):
    page.goto('https://www.proficosmetics.ru/auth/')  # 60 секунд
    page.wait_for_timeout(1000)
    page.fill('#login', 'kandja@mail.ru')
    page.fill('#password', 'S666999s')
    page.click('form button')

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
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.set_viewport_size({"width": 1800, "height": 900})
        page.evaluate("document.body.style.zoom='25%'")
 
        url = xml_unpack(operation_id)
        if url is None:
            print(f'Галерея, позиция {item} - пустая')
            browser.close()
            return
        relog(page)
        try:
            page_dict = {}
            initiate_dict(page_dict)
            print(f'Работа с позицией {item}')
            time.sleep(0.1)
            page.goto(url[0])
            link = url[0]
            brand_name = get_brand_name(page)
            product_clear_name, volume = get_clear_name_and_vol(page)
            artikul = get_article(page)
            price = get_price(page)
            add_new_element(page_dict, brand_name, artikul, product_clear_name, volume, link, price, True, item)
            browser.close()
        except Exception as e:
            browser.close()
            raise e
            return

        invalid_chars = r'[\/:*?"<>|]'
        pd.DataFrame(page_dict).to_excel(fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\gallery_{re.sub(invalid_chars, '_', item)}.xlsx")

if __name__ == '__main__':
    parse('Сыворотка биоботаническая против выпадения и для стимуляции роста волос / SYSTEM 4, 150 мл', False)