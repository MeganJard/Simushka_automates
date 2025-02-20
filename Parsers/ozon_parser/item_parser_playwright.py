from playwright.sync_api import sync_playwright
import pandas as pd
from datetime import datetime
import re
from googlesearch import search
from random import choice
import xml.etree.ElementTree as ET

PLOSHADKA = 'ozon.ru'
proxies = ["http://21585V:zjKmJR@5.8.83.151:8000",
           'http://3CNEf9:HVH50t@46.8.59.223:8000',
           'http://3CNEf9:HVH50t@46.8.58.68:8000',
           'http://3CNEf9:HVH50t@46.8.59.108:8000',
           'http://3CNEf9:HVH50t@46.8.59.108:8000',
           'http://3CNEf9:HVH50t@46.8.59.108:8000'
]
def yandex_search(query, platform):
    while True:
        try:
            # Выполняем поиск в Google

            search_results = list(search(query, proxy=choice(proxies)))  # num — количество результатов, pause — задержка между запросами
            
            # Фильтруем результаты по платформе и пути /product/
            answer = []
            for link in search_results:
                if platform in link and '/product/' in link:
                    answer.append(link)
            
            # Возвращаем первые 5 уникальных ссылок
            return list(set(answer))[:10]
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            continue

def initiate_dict(page_dict):
    keys = [
        'Артикул площадки', 'Бренд', 'Есть в наличии',
        'Название товара на площадке', 'Объем', 'Площадка',
        'Ссылка на товар', 'Цена', 'Цена со скидкой',
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
    page_dict['Цена'].append(price[1] if len(price) > 1 else '')
    page_dict['Цена со скидкой'].append(price[0] if len(price) > 0 else '')
    page_dict['Есть в наличии'].append(True)
    page_dict['Дата парсинга'].append(str(datetime.today().strftime("%Y-%m-%d")))
    page_dict['Название товара наше'].append(our_name)

def get_article(page):
    try:
        return page.query_selector('//*[@id="layoutPage"]/div[1]/div[3]/div[2]/div/div/div/div[2]/button[1]/div').text_content().split(':')[1].strip()
    except Exception:
        return ''

def get_clear_name_and_vol(page):
    try:
        page.wait_for_selector('//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[1]/div[1]/div[2]/div/div/div/div[1]/h1', timeout=5000)
        product_full_name = page.query_selector('//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[1]/div[1]/div[2]/div/div/div/div[1]/h1').text_content()
        parts = product_full_name.split()
        if parts[-1] not in ['мл', 'гр', 'г'] and not parts[-2].isdigit():
            return product_full_name, None
        return ' '.join(parts[:-2]), ' '.join(parts[-2:])
    except Exception:
        return '', ''

def get_price(page):
    price_selectors = [
        '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[3]/div/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span',
        '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span[1]',
        '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span',
        '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/span[1]'
    ]
    
    prices = []
    for selector in price_selectors:
        element = page.query_selector(selector)
        if element:
            text = element.text_content().replace('₽', '').replace(' ', '').replace('\u2009', '')
            if text.isdigit():
                prices.append(int(text))
    return sorted(prices)[:2]

def parse_product(context, page_dict, item_block_href, our_name):
    page = context.new_page()
    try:
        page.goto(item_block_href)

        
        title, volume = get_clear_name_and_vol(page)
        article = get_article(page)
        price = get_price(page)
        
        if price:
            add_new_element(
                page_dict=page_dict,
                brand=None,
                article=article,
                title=title,
                volume_1=volume,
                item_block_href=item_block_href,
                price=price,
                vnal=True,
                our_name=our_name
            )
    except Exception as e:
        print(f'Ошибка при парсинге товара: {e}')
    finally:
        page.close()
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

        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--disable-infobars",
                "--disable-extensions"
            ]
        )

        # Создание контекста с настройками
        context = browser.new_context(
            viewport={'width': 1800, 'height': 900},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            bypass_csp=True
        )

        # Создание страницы и отключение navigator.webdriver
        page = context.new_page()
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
         """)
        page = context.new_page()


        next_line = '\n'
        print(f'Паршу {item} по ссылкам {next_line.join(urls)}')
        if not urls:
            return
        page_dict = {}
        initiate_dict(page_dict)

        for url in urls:
            try:
                parse_product(context, page_dict, url, item)
            except Exception as e:
                print(f'Ошибка при обработке URL {url}: {e}')
                continue

        browser.close()

        invalid_chars = r'[\/:*?"<>|]'
        try:
            if len(page_dict['Цена']) > 0:
                pd.DataFrame(page_dict).to_excel(
                 fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\{PLOSHADKA}_{re.sub(invalid_chars, '_', item)}.xlsx")
        except Exception as e:
            print(f"Error saving file: {e}")

            
# def parse(item, clear_cache=True, url=''):
#     urls = yandex_search(f'ozon.ru/product {item}', 'ozon.ru') if not url else [url]
#     if not urls:
#         return

#     with sync_playwright() as p:
#         browser = p.chromium.launch(
#             headless=False,
#             args=[
#                 "--disable-blink-features=AutomationControlled",
#                 "--start-maximized",
#                 "--disable-infobars",
#                 "--disable-extensions"
#             ]
#         )

#         # Создание контекста с настройками
#         context = browser.new_context(
#             viewport={'width': 1800, 'height': 900},
#             user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
#             bypass_csp=True
#         )

#         # Создание страницы и отключение navigator.webdriver
#         page = context.new_page()
#         page.add_init_script("""
#             Object.defineProperty(navigator, 'webdriver', {
#                 get: () => undefined
#             });
#         """)

#         # Установка масштаба (пример)
#         page.evaluate("document.body.style.zoom='25%'")
#         page_dict = {}
#         initiate_dict(page_dict)
#         print(f'Обработка позиции: {item}')

#         for url in urls:
#             try:
#                 parse_product(context, page_dict, url, item)
#             except Exception as e:
#                 print(f'Ошибка при обработке URL {url}: {e}')
#                 continue

#         context.close()
#         browser.close()

#     if page_dict.get('Цена'):
#         invalid_chars = r'[\/:*?"<>|]'
#         safe_name = re.sub(invalid_chars, '_', item)
#         pd.DataFrame(page_dict).to_excel(fr'C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\ozon_{safe_name}.xlsx', index=False)

if __name__ == '__main__':
    parse('Finish Ultimate All in 1 капсулы таблетки для посудомоечной машины, 75 шт лимон')