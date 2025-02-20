
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

PLOSHADKA = 'ozon.ru'

global screenshot_counter
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
    driver.implicitly_wait(0.5)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.set_window_size(1800, 900)
    counter = 0
    try:
        driver.get(f"https://www.google.ru/search?q={query.replace('/', '')}")
        time.sleep(1)
        links = driver.find_elements("xpath", "//a[@href]")
        results = [link.get_attribute("href") for link in links]
        driver.close()
        answer = []

        for link in results:
            try:
                if platform in link and '/product/' in link:
                    answer.append(link)
            except Exception:
                print('Ошибка на 44 строке')
        return list(set(answer[:5]))[:5]
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
    driver.implicitly_wait(2)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_brand(driver):
    return None

def get_plosh():
    return PLOSHADKA

def get_article(driver):
    try: 
        article = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[3]/div[2]/div/div/div/div[2]/button[1]/div').text.split(':')[1]
    except Exception as e:
        article = ''
    return article

def get_clear_name_and_vol(driver):
    try:
        product_full_name = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[1]/div[1]/div[2]/div/div/div/div[1]/h1').text
        if product_full_name.split()[-1] != 'мл' and product_full_name.split()[-1] != 'гр' and product_full_name.split()[-1] != 'г' and (not product_full_name.split()[-2].isdigit()):
            product_clear_name = product_full_name
            volume = None
        else:
            product_clear_name = ' '.join(product_full_name.split()[:-2])
            volume = ' '.join(product_full_name.split()[-2:])
        return product_clear_name, volume
    except Exception:
        return '', ''



def get_price(driver):
    prices = []
    all_links_classes = ['//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[3]/div/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span',
                         '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span[1]',
                         '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[3]/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span[2]',
                         '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span'
                         '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/span[1]',
                         '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div[1]/div[1]/div/div/div[1]/div[2]/div/div[1]/span[2]',
                         '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span',
                         '//*[@id="layoutPage"]/div[1]/div[3]/div[3]/div[2]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span',
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
    




def parse_product(driver, page_dict, item_block_href, our_name):
    driver.get(item_block_href)
    driver.execute_script("document.body.style.zoom='25%'")
    time.sleep(0.5)
    brand = get_brand(driver)
    title, volume = get_clear_name_and_vol(driver)
    article = get_article(driver)
    price = get_price(driver)
    vnal = True
    if len(price) != 0:
        add_new_element(page_dict, brand,article,title, volume, item_block_href, price, vnal, our_name)




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
        driver.implicitly_wait(2)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        delete_cache(driver)
        driver.close()
    urls = yandex_search(f'+ozon inurl:product +{item}', 'ozon.ru') if url == '' else [url]
    print(urls)
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
    print(f'Работа с позицией {item}')

    print(f'urls: {urls}')
    for url in urls:
        captcha_counter = 0
        try:
            parse_product(driver, page_dict, url, item)

        except Exception as e:
           # raise e
            continue
    
    driver.close()        



    
    invalid_chars = r'[\/:*?"<>|]'
    # Замена недопустимых символов на подчеркивание
    if len(page_dict['Цена']) > 0:
        pd.DataFrame(page_dict).to_excel(fr"C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder\ozon_{re.sub(invalid_chars, '_', item)}.xlsx")



if __name__ == '__main__':
    counter = 0


    while True:
        counter += 1

        parse('samsung galaxy s24 ultra', clear=True, url='')
        print(counter)