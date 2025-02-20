from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import selenium
from selenium import webdriver
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime
PLOSHADKA = 'ibt.ru'

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
def get_all_items(driver):

    counter = 0
    while True:
        try:
            start_time = time.time()
            current_time = time.time()
            while current_time - start_time <= 360:
                driver.execute_script('window.scrollBy(0, document.body.scrollHeight);')
                time.sleep(0.1)
                try:
                    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[@id="showMoreBlockID"]/button'))
                except Exception:
                    pass
                current_time = time.time()  # Обновляем текущее время
            return [i.get_attribute('href') for i in driver.find_element(By.CLASS_NAME, 'catalog-product-list__list').find_elements(By.TAG_NAME, 'a')]
        except Exception as e:
            if counter == 10:
                print('ELEMENTS HREFS ARE NOT PARSED')
                return []
            counter += 1
            time.sleep(30)
def parse_element(driver, product_href, brand_name, page_dict):
    driver.get(product_href)
    time.sleep(3)

    title = driver.find_element(By.CLASS_NAME, 'product-detail-panel__hl').text.split(',')[0]
    brand = brand_name
    try:
        article = driver.find_element(By.XPATH, '//*[@id="app"]/main/section/section[1]/div/div[2]/div[1]/div/div/span').text
    except Exception:
        article = 'No'

    volume = driver.find_element(By.CLASS_NAME, 'product-detail-panel__hl').text.split(',')[-1] if 'л' in driver.find_element(By.CLASS_NAME,
                                                                                                                              'product-detail-panel__hl').text.split(
        ',')[-1] or 'г' in driver.find_element(By.CLASS_NAME, 'product-detail-panel__hl').text.split(',')[-1] else ''
    volume = volume if len(volume.split()) <= 2 else ''
    try:
        price_lower = driver.find_element(By.CLASS_NAME, 'product-cart-panel__info-prices').text.split('\n')[0]
    except Exception:
        price_lower = ''
    try:
        price_bigger = driver.find_element(By.CLASS_NAME, 'product-cart-panel__info-prices').text.split('\n')[1]
    except Exception:
        price_bigger = ''
    print(volume)
    add_new_element(page_dict, brand, article, title, volume, product_href, [price_lower, price_bigger], True)

    pd.DataFrame(page_dict).to_excel(fr'C:/Users/admin/PycharmProjects/pythonProject/price_parsers/parsers_output/BT_parser/{brand_name}.xlsx')

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

def parse(brand_name):
    driver = webdriver.Chrome()
    url = f'https://ibt.ru/brands/{brand_name}/?orderField=popularity&orderDirection=desc'
    delete_cache(driver)
    print(url)
    driver.get(url)
    driver.execute_script("document.body.style.zoom='25%'")
    all_products_hrefs = get_all_items(driver)
    print(len(all_products_hrefs))
    page_dict = dict()
    initiate_dict(page_dict)

    for product_href in all_products_hrefs:
        print(product_href)
        counter = 0
        while True:
            try:
                parse_element(driver, product_href, brand_name, page_dict)
                break
            except Exception as e:
                if counter == 30:
                    print('Something went wrong')
                    break
                time.sleep(30)
                counter += 1




