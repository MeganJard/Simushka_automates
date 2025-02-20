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

PLOSHADKA = 'wildberries.ru'



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
    counter = 0

    try:
        driver.get(f"https://www.google.ru/search?q={query.replace('/', '')}")
        time.sleep(0.2)
        links = driver.find_elements("xpath", "//a[@href]")
        results = [link.get_attribute("href") for link in links]
        driver.close()
        answer = []
        for link in results:
            try:
                if platform in link and 'catalog' in link and len(link.split('/')) == 6:
                    answer.append(link)
            except Exception:
                pass

        return list(set(answer[:5]))
    except Exception as e:
        driver.close()
        return


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
    return driver


def get_brand_name(driver):
    try:
        time.sleep(20)
        return driver.find_element(By.XPATH, '/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[9]/div[1]/a').text
    except Exception as e:
        raise (e)
        print("No brand name found")
        return None


def get_article(url):
    try:
        return url.split('/')[4]
    except Exception as e:
        print('No article found')
        return None


def get_volume(driver):
    try:
        volume = driver.find_element(By.CLASS_NAME, 'product-params__table').text
    except Exception as e:
        volume = None
    return volume


def get_price(driver):
    prices = []
    all_links_classes = ['/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[14]/div/div[1]/div[1]/div/div/div/p/span/span',
                        '/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[14]/div/div[1]/div[1]/div/div/div/p/span/ins',
                        '/html/body/div[1]/main/div[2]/div[2]/div[3]/div/div[3]/div[14]/div/div[1]/div[1]/div/div/div/p/del/span'
                         ]
    for link in all_links_classes:
        try:
            val = driver.find_element(By.XPATH, link).text
            prices.append(val)
        except Exception:
            prices.append('')
    # for xpath in ['//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[1]/div[3]/div/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span']:
    #     try:
    #         prices.append(driver.find_element_by_xpath(xpath).text)
    #     except Exception as e:
    #         pass
    print(prices)
    prices = list([i.replace('₽', '').replace(' ', '').replace('\u2009', '') if not (i is None) else '' for i in prices])
    prices = list([int(i) for i in prices if i != ''])
    print(prices)
    return sorted(prices)[:2]

def get_product_name(driver):
    return driver.find_element(By.CLASS_NAME, 'product-page__title').text




def parse(item, clear, url=''):
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
    urls = yandex_search(f'wildberries вайлдберриз {item}', PLOSHADKA) if url == '' else [url]
    if urls == []:
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

    print(urls)
    for url in urls:
        captcha_counter = 0
        try:
            driver.get(url)
            time.sleep(0.5)
            link = url
            brand_name = get_brand_name(driver)
            product_name = get_product_name(driver)
            artikul = get_article(url)
            price = get_price(driver)
            volume = get_volume(driver)
            add_new_element(page_dict, brand_name, artikul, product_name, volume, link, price, True, item)

        except Exception as e:
            continue
        
    driver.close()     

    invalid_chars = r'[\/:*?"<>|]'
    # Замена недопустимых символов на подчеркивание
    try:
        pd.DataFrame(page_dict).to_excel(
            fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\{PLOSHADKA}_{re.sub(invalid_chars, '_', item)}.xlsx")
    except:
        pass


if __name__ == '__main__':
    parse('lol', False, 'https://www.wildberries.ru/catalog/208206483/detail.aspx')