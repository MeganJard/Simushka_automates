
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

PLOSHADKA = 'goldapple.ru'
def yandex_search(query, platform):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")

    # Создание экземпляра драйвера с заданными настройками
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
   # driver.execute_script("document.body.style.zoom='25%'")
    driver.implicitly_wait(1.5)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.set_window_size(1800, 900)


    try:
        driver.get(f"https://www.google.ru/search?q={query.replace('/', '')}")
        time.sleep(0.1)
        links = driver.find_elements("xpath", "//a[@href]")
        results = [link.get_attribute("href") for link in links]
        driver.close()
        for link in results[:40]:
            if platform in link and len(link.split('/')) == 4 and link.split('/')[3] != '':
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
    price = list([i.replace('₽', '').replace(' ', '') if not(i is None) else '' for i in price])
    is_BYN = 'BYN' in price[0] 
    price = list([i.replace('BYN', '') for i in price])
    if price[0].isdigit():
        price[0] = int(price[0])
    if price[1].isdigit():
        price[1] = int(price[1])
    if type(price[0]) == int and type(price[1]) == int:
        price = list(sorted(price, reverse=True))
    if price[0] != int and price[1] == int:
        price[0], price[1] = price[1], price[0] 
    
    if is_BYN:
        price[0] *= 28.77
        price[1] *= 28.77
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
    time.sleep(0.5)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(0.5)
    driver.get('chrome://settings/clearBrowserData')  # for old chromedriver versions use cleardriverData
    time.sleep(0.5)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 1 + Keys.ENTER * 1)  # send right combination
    actions.perform()
    time.sleep(0.5)
    driver.close()  # close this tab
    driver.switch_to.window(driver.window_handles[0])  # switch back





def reinit(driver, ctr):
    driver = driver_init()
    return driver



def get_plosh():
    return PLOSHADKA


def get_brand(driver):
    return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/div/div/h1/a').text


def get_article(driver):
    return ''


def get_title(driver):
    return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/div/div/h1/span').text


def get_price(driver):
    try:
        usual_price = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[1]/div[1]').text
        offer_price = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[2]/div[1]').text
    except Exception:
        try:
            usual_price = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[1]/div').text
            offer_price = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div[2]/div[1]').text
        except Exception:
            usual_price = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[2]/div[1]/div').text
            offer_price = None
    return [usual_price, offer_price]


def get_vnal(driver):
    return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[3]/div[1]').text != 'нет в наличии'


def get_one_volume(driver):
    try:
        return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[1]/div/div[1]').text
    except Exception:
        return None

def press_cross(driver):
    try:
        driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[4]/aside[1]/div[2]/div/div/button').click()  # pressing cross button for location form exit
    except Exception as e:
        pass


def press_grid(driver):
    try:
        driver.find_element(By.XPATH,
                            '//*[@id="__layout"]/div/main/div[1]/div/div/div/div[2]/button/div[2]/i[2]').click()  # pressing grid view button
    except Exception as e:
        pass

def get_volume(driver):
    try:
        volume = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[1]/div[1]').text
    except Exception as e:
        volume = ''
    try:
        color = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[1]/div[2]/div[1]/div/span/div').text
    except Exception as e:
        color = ''
    return volume + '\n' + color


def parse_product(driver, page_dict, item_block_href, our_name):
    driver.get('https://goldapple.ru')
    time.sleep(4)
    driver.get(item_block_href)
    time.sleep(2)
    driver.execute_script("document.body.style.zoom='25%'")
    title = get_title(driver)
    print('\n\nTITLE', title, '\n\n')
    brand = get_brand(driver)
    article = get_article(driver)
    price = get_price(driver)
    volume = get_volume(driver)
    vnal = get_vnal(driver)
    add_new_element(page_dict, brand,article,title, volume, item_block_href, price, vnal, our_name)

def driver_init():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    import time
    import random
    from selenium_stealth import stealth
    chrome_options = Options()

# Отключение автоматизации и других функций, которые могут выдать бота
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=en-US")  # Установка языка браузера
    # chrome_options.add_argument('--profile-directory=Profile 1')
    # chrome_options.add_argument("user-data-dir=C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\User Data\\")
    # Отключение автоматического управления WebDriver
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Случайный User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        # Добавьте другие User-Agent'ы
    ]
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    # Создание экземпляра драйвера с заданными настройками
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Скрытие WebDriver свойства
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Установка случайного масштаба страницы
    zoom_level = random.uniform(0.5, 1.5)
    driver.execute_script(f"document.body.style.zoom='{zoom_level * 100}%'")

    # Установка случайного размера окна
    width = random.randint(1200, 1800)
    height = random.randint(800, 1200)
    driver.set_window_size(width, height)
    stealth(
    driver,
    languages=["en-US", "en"],
    vendor="Google Inc.",
    platform="Win32",
    webgl_vendor="Intel Inc.",
    renderer="Intel Iris OpenGL Engine",
    fix_hairline=True,
        )
    return driver


def parse(item, clear, url=''):
    driver = driver_init()
    if clear:
        delete_cache(driver)


    invalid_chars = r'[\/:*?"<>|]'+"'"
   # url = url.replace('.ru', '.by')
    url = yandex_search(f'золотое яблоко goldapple {re.sub(invalid_chars, " ", item)}', 'goldapple.ru') if url == '' else url
    if url is None:
        return

    page_dict = {}
    initiate_dict(page_dict)
    print(f'Работа с позицией {item}')
    print(url)
    try:
        parse_product(driver, page_dict, url, item)
        driver.close()
    except Exception as e:
        raise(e)
        driver.close()
        return
           




    # Замена недопустимых символов на подчеркивани
    invalid_chars = r'[\/:*?"<>|]'
    # Замена недопустимых символов на подчеркивание
    try:
        pd.DataFrame(page_dict).to_excel(
            fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\{PLOSHADKA}_{re.sub(invalid_chars, '_', item)}.xlsx")
        time.sleep(1.5)
    except:
        pass

if __name__ == '__main__':

    parse("L'ARTISAN PARFUMEUR memoire de roses", False, 'https://goldapple.ru/19000000557-original-pomade')