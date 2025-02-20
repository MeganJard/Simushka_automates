
from selenium.webdriver.common.by import By
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

PLOSHADKA = 'ibt.ru'
def yandex_search(query, platform):
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
    driver.implicitly_wait(3)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.set_window_size(1800, 900)

    try:
        driver.get(f"https://www.google.ru/search?q={query.replace('/', '')}")
        time.sleep(1)
        links = driver.find_elements("xpath", "//a[@href]")
        results = [link.get_attribute("href") for link in links]
        driver.close()
        for link in results[:40]:
            if platform in link and 'product' in link and len(link.split('/')) == 6:
                return link
        return None
    except Exception as e:
        driver.close()
        return None






def initiate_dict(page_dict):
    page_dict['Артикул площадки'] = []
    page_dict['Бренд'] = []
    page_dict['Есть в наличии'] = []
    page_dict['Название товара на площадке'] = []
    page_dict['Объем'] = []
    page_dict['Площадка'] = []
    page_dict['Ссылка на товар'] = []
    page_dict['Цена'] = []
    page_dict['Цена со скидкой'] = []
    page_dict['Название товара наше'] = []
    page_dict['Дата парсинга'] = []
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
    page_dict['Есть в наличии'].append(True)
    page_dict['Дата парсинга'].append(str(datetime.today().strftime("%Y-%m-%d")))
    page_dict['Название товара наше'].append(our_name)


def delete_cache(driver):
    driver.execute_script("window.open('');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    driver.get('chrome://settings/clearBrowserData')  # for old chromedriver versions use cleardriverData
    time.sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 1 + Keys.ENTER * 1)  # send right combination
    actions.perform()
    time.sleep(2)
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
    driver.implicitly_wait(3)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    relog(driver)
    return driver



def get_brand_name(driver):
    try:

        return driver.find_element(By.CLASS_NAME, 'product-view__header-detail-brand').find_element(By.TAG_NAME, 'a').get_attribute('href').split('/')[4]
    except Exception as e:
        raise(e)
        print("No brand name found")
        return None

def get_article(driver):
    try:
        return driver.find_element(By.XPATH, '//*[@id="app"]/main/section/section[1]/div/div[2]/div[1]/div/div/span').text
    except Exception:
        print("No article")
        return None

def get_volume(driver):
    volume = driver.find_element(By.CLASS_NAME, 'product-detail-panel__hl').text.split(',')[-1] if 'л' in driver.find_element(By.CLASS_NAME, 'product-detail-panel__hl').text.split(',')[-1] or 'г' in driver.find_element(By.CLASS_NAME, 'product-detail-panel__hl').text.split(',')[-1] else ''
    if len(volume.split()) <= 2:
        return volume
    else:
        print("No volume")
        return None

def get_price(driver):
    try:
        price_lower = driver.find_element(By.CLASS_NAME, 'product-cart-panel__info-prices').text.split('\n')[0]
    except Exception:
        price_lower = ''
    try:
        price_bigger = driver.find_element(By.CLASS_NAME, 'product-cart-panel__info-prices').text.split('\n')[1]
    except Exception:
        price_bigger = ''
    if price_lower == '' and price_bigger == '':
        raise Exception('No price available')
    return [price_lower, price_bigger]

def get_product_name(driver):
    return driver.find_element(By.CLASS_NAME, 'product-detail-panel__hl').text.split(',')[0]
def relog(driver):
    driver.get('https://ibt.ru/')
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="app"]/header/div[2]/div/div[3]/div[1]/div/div/button').click()
    driver.find_element(By.NAME, 'phone').send_keys('+7 (936) 237-31-89')
    time.sleep(1)
    driver.find_element(By.NAME, 'password').send_keys('827617')
    time.sleep(1)
    driver.find_element(By.XPATH, '//*[@id="v-tab--panel1"]/div/form/div[3]/button[1]').click()
    time.sleep(1)


def parse(item, clear, url):
    if clear:
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
        driver.implicitly_wait(3)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        delete_cache(driver)
        driver.close()
    url = yandex_search(f"бессовестно талантливый 'ibt' inurl:product {item}", 'ibt.ru') if url == '' else url
    if url is None:
        return
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
    driver.implicitly_wait(3)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.set_window_size(1800, 900)

    page_dict = {}
    initiate_dict(page_dict)
    print(f'Работа с позицией {item}')
    print(url)
    #relog(driver)

    try:
        driver.get(url)
        time.sleep(1.5)
        link = url
        brand_name = get_brand_name(driver)
        product_name = get_product_name(driver)
        artikul = get_article(driver)
        price = get_price(driver)
        volume = get_volume(driver)
        add_new_element(page_dict, brand_name, artikul, product_name, volume, link, price, True, item)
        driver.close()
    except Exception as e:
        driver.close()
        return 




    invalid_chars = r'[\/:*?"<>|]'
    # Замена недопустимых символов на подчеркивание

    pd.DataFrame(page_dict).to_excel(fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\ibt_{re.sub(invalid_chars, '_', item)}.xlsx")


if __name__ == '__main__':
    parse('Kydra Le Salon Крем-краска для волос тонирующая KydraSofting Tone-On-Tone Ammonia Free Hair Color Treatment Cream, махагон Mahogany, 60 мл', False)