from selenium.webdriver.common.by import By
import time
from selenium import webdriver
import pandas as pd
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime

PLOSHADKA = 'ozon.ru'



#ссылка на категорию, которую хотим запарсить

def get_plosh():
    return PLOSHADKA

def initiate_dict(page_dict):
    page_dict['Площадка'] = []
    page_dict['Бренд'] = []
    page_dict['Артикул площадки'] = []
    page_dict['Название товара'] = []
    page_dict['Объем'] = []
    page_dict['Ссылка на товар'] = []
    page_dict['Цена'] = []
    page_dict['Цена со скидкой'] = []
    page_dict['Есть в наличии'] = []
    page_dict['Дата парсинга'] = []
    page_dict['Кол-во в наличии'] = []
    return page_dict


def add_new_element(page_dict, brand, article, title, volume_1, item_block_href, price, vnal):
    price = list([i.replace('₽', '').replace(' ', '') for i in price])
    if price[0].isdigit() and price[1].isdigit():
        price = list(int(i) for i in price)
    price = list(sorted(price, reverse=True))
    print(price)
    page_dict['Площадка'].append(PLOSHADKA)
    page_dict['Бренд'].append(brand)
    page_dict['Артикул площадки'].append(article)
    page_dict['Название товара'].append(title)
    page_dict['Объем'].append(volume_1)
    page_dict['Ссылка на товар'].append(item_block_href)
    page_dict['Цена'].append(price[0])
    page_dict['Цена со скидкой'].append(price[1])
    page_dict['Есть в наличии'].append(vnal)
    page_dict['Дата парсинга'].append(str(datetime.today().strftime("%Y-%m-%d")))
    page_dict['Кол-во в наличии'].append(None)

def delete_cache(driver):
    driver.execute_script("window.open('');")
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    driver.get('chrome://settings/clearBrowserData') # for old chromedriver versions use cleardriverData
    time.sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 1 + Keys.ENTER * 1) # send right combination
    actions.perform()
    time.sleep(2)
    driver.close() # close this tab
    driver.switch_to.window(driver.window_handles[0]) # switch back


def get_article(driver):
    return driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[2]/div/div/div/div[2]/button[1]/div').text.split(':')[1]
def get_clear_name_and_vol(driver):
    product_full_name = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[1]/div[1]/div[2]/div/div[1]/h1').text
    if product_full_name.split()[-1] != 'мл' and product_full_name.split()[-1] != 'гр' and product_full_name.split()[-1] != 'г' and (not product_full_name.split()[-2].isdigit()):
        product_clear_name = product_full_name
        volume = None
    else:
        product_clear_name = ' '.join(product_full_name.split()[:-2])
        volume = ' '.join(product_full_name.split()[-2:])
    return product_clear_name, volume




def get_price(driver):
    try:
        lower_price = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div/div/div[1]/span[1]').text
        def_price = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div/div/div[1]/span[2]').text
        return lower_price, def_price
    except Exception:
        lower_price = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[1]/button/span/div/div[1]/div/div/span').text
        def_price = driver.find_element(By.XPATH, '//*[@id="layoutPage"]/div[1]/div[4]/div[3]/div[2]/div[1]/div/div/div[1]/div/div/div[1]/div[2]/div/div[1]/span[1]').text
        return lower_price, def_price
    raise Exception('No price found')

def reinit(driver):
    counter = 0
    while True:
        try:
            driver.close()
            time.sleep(100)
            driver = webdriver.Chrome()
            driver.execute_script("document.body.style.zoom='25%'")
            driver.set_window_size(1800, 900)
            driver.implicitly_wait(2)
            return driver
        except Exception:
            if counter == 20:
                raise Exception('ALL CRASHED')
            time.sleep(100)
            counter += 1


def get_all_hrefs(driver, is_grid):
    if is_grid:
        return [i.find_element(By.TAG_NAME, 'a').get_attribute('href') for i in driver.find_element(By.XPATH, '//*[@id="paginatorContent"]/div').find_elements(By.CLASS_NAME, 'iy1')]
    else:
        return [i.find_element(By.TAG_NAME, 'a').get_attribute('href') for i in driver.find_element(By.XPATH, '//*[@id="paginatorContent"]/div').find_elements(By.CLASS_NAME, 'i3y')]

def parse(category, is_grid):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(
        '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
    driver = webdriver.Chrome(options=chrome_options)

    driver.implicitly_wait(3)

    delete_cache(driver)
    time.sleep(5)
    url = f'https://www.ozon.ru/search/?from_global=true&text={category}/'
    driver.get(url)
    driver.set_window_size(1800, 900)
    driver.execute_script("document.body.style.zoom='25%'")

    page_dict = {}
    initiate_dict(page_dict)

    for page_index in range(1, 1000):
        time.sleep(5)

        driver.get(url+f'?page={page_index}')

        all_hrefs = [block.find_element(By.TAG_NAME, 'a').get_attribute('href') for block in driver.find_elements(By.CLASS_NAME, 'photo')]
        while len(all_hrefs) == 0:
            print('CAPTCHA DETECTED')
            driver.close()
            time.sleep(100)
            driver = webdriver.Chrome()
            driver.execute_script("document.body.style.zoom='25%'")
            driver.set_window_size(1800, 900)
            driver.implicitly_wait(2)
            driver.get(url + f'p{page_index}')
            all_hrefs = [block.find_element(By.TAG_NAME, 'a').get_attribute('href') for block in driver.find_elements(By.CLASS_NAME, 'photo')]

        captcha_counter = 0

        for item_block_href in all_hrefs:
            while True:
                try:
                    time.sleep(0.5)
                    link = item_block_href
                    brand_name = category
                    product_clear_name, volume = get_clear_name_and_vol(driver)
                    artikul = get_article(driver)
                    price = get_price(driver)
                    add_new_element(page_dict, brand_name, artikul, product_clear_name, volume, link, price, True)
                    pd.DataFrame(page_dict).to_excel(fr'../parsers_output/gallery_cosm/{category}.xlsx')
                except Exception as e:
                    print('CAPTCHA DETECTED')
                    if captcha_counter == 2:
                        captcha_counter = 0
                        break
                    captcha_counter += 1
                    raise e
                    driver = reinit(driver)
    driver.close()

parse('babyliss', True)