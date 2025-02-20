

import time
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import re
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
PLOSHADKA = 'proficosmetics.ru'


# ссылка на категорию, которую хотим запарсить

def get_plosh():
    return PLOSHADKA


def yandex_search(query, platform):
    driver = webdriver.Chrome()
    counter = 0
    try:
        driver.get(f"https://www.google.ru/search?q={query.replace('/', '')}")
        time.sleep(1)
        links = driver.find_elements("xpath", "//a[@href]")
        results = [link.get_attribute("href") for link in links]
        driver.close()
        for link in results[:40]:
            if platform in link and link.count('/') == 5:
                try:
                    if link.split('/')[4].isdigit():
                        print(link)
                        return link
                    else:
                        print('Отсев по признаку не число после каталога')
                except Exception as e:
                    print('адрес не разбился на пять частей')
                    pass
        return None
    except Exception as e:
        driver.close()
        return None





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


def delete_cache(driver):
    driver.execute_script("window.open('');")
    time.sleep(0.3)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(0.3)
    driver.get('chrome://settings/clearBrowserData')  # for old chromedriver versions use cleardriverData
    time.sleep(0.3)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 1 + Keys.ENTER * 1)  # send right combination
    actions.perform()
    time.sleep(0.3)
    driver.close()  # close this tab
    driver.switch_to.window(driver.window_handles[0])  # switch back





def reinit(driver, ctr):
    delete_cache(driver)
    driver.close()
    time.sleep(2)
    # Отключение автоматических уведомлений
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    # Создание экземпляра драйвера с заданными настройками
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("document.body.style.zoom='25%'")
    driver.set_window_size(1800, 900)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.implicitly_wait(5)
    return driver



def get_brand_name(driver):
    return driver.find_element(By.CLASS_NAME, 'product_main_desc').find_element(By.TAG_NAME, 'h4').find_element(By.TAG_NAME, 'span').text

def get_article(driver):
    return driver.find_element(By.CLASS_NAME, 'kr_product_info').find_elements(By.TAG_NAME, 'p')[0].text.split(':')[1]
def get_clear_name_and_vol(driver):
    product_full_name = driver.find_element(By.CLASS_NAME, 'product_main').find_element(By.TAG_NAME, 'h1').text
    if product_full_name.split()[-1] != 'мл' and product_full_name.split()[-1] != 'гр' and product_full_name.split()[-1] != 'г':
        product_clear_name = product_full_name
        volume = None
    else:
        product_clear_name = ' '.join(product_full_name.split()[:-2])
        volume = ' '.join(product_full_name.split()[-2:])
    return product_clear_name, volume

def get_price(driver):
    old_price_block = driver.find_elements(By.CLASS_NAME, 'old_price-number')
    if len(old_price_block) > 0:
        old_price = old_price_block[0].text
    else:
        old_price = ''
    return old_price, ''.join(driver.find_element(By.CLASS_NAME, 'new_price').text.split()[:-1])

def relog(driver):
    driver.get('https://www.proficosmetics.ru/auth/')
    driver.find_element(By.XPATH, '//*[@id="login"]').send_keys('kandja@mail.ru')
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys('S666999s')
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div/form/button').click()


def parse(item, clear, url):
    if clear:
        driver = reinit(webdriver.Chrome(), 0)
    else:
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")

        # Создание экземпляра драйвера с заданными настройками
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("document.body.style.zoom='25%'")
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(5)

    url = yandex_search(f'галерея косметики proficosmetics {item}', 'proficosmetics.ru') if url == '' else url
    if url is None:
        driver.close()
        return

    try:
        relog(driver)
        page_dict = {}
        initiate_dict(page_dict)
        print(f'Работа с позицией {item}')
        time.sleep(0.1)
        driver.get(url)
        link = url
        brand_name = get_brand_name(driver)
        product_clear_name, volume = get_clear_name_and_vol(driver)
        artikul = get_article(driver)
        price = get_price(driver)
        add_new_element(page_dict, brand_name, artikul, product_clear_name, volume, link, price, True, item)
        driver.close()
    except Exception as e:
        driver.close()
        return




    invalid_chars = r'[\/:*?"<>|]'
    # Замена недопустимых символов на подчеркивание

    pd.DataFrame(page_dict).to_excel(fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\gallery_{re.sub(invalid_chars, '_', item)}.xlsx")


if __name__ == '__main__':
    parse('Сыворотка биоботаническая против выпадения и для стимуляции роста волос / SYSTEM 4, 150 мл', False)
