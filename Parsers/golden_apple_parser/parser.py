from selenium.webdriver.common.by import By
import time
import selenium
from selenium import webdriver
import pandas as pd
from time import strftime
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ChromeOptions
PLOSHADKA = 'goldapple.ru'


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


def get_plosh():
    return PLOSHADKA


def get_brand(driver):
    return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/div/div/h1/a').text


def get_article(driver):
    return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[4]/div[2]/div[1]/div[2]/div/div/div/div/div[2]').text.split(':')[1].replace(' ', '')


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
    return usual_price, offer_price


def get_vnal(driver):
    return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[3]/div[1]').text != 'нет в наличии'


def get_one_volume(driver):
    try:
        return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[1]/div/div[1]').text
    except Exception:
        return None


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


def parse_product(driver, page_dict, item_block_href):
    brand = get_brand(driver)
    title = get_title(driver)

    all_volume_links = driver.find_elements(By.XPATH, '//*[@id="__layout"]/div/main/article/div[1]/div[1]/form/div[1]/div/div[2]/div')
    if len(all_volume_links) != 0:
        vol_buttons = all_volume_links[0].find_elements(By.TAG_NAME, 'label')
        if len(vol_buttons):
            for volume_button in vol_buttons:
                press_cross(driver)
                try:
                    driver.execute_script("arguments[0].click();", volume_button)
                except Exception as e:
                    print(e)
                    pass
                article = get_article(driver)
                price = get_price(driver)
                volume = volume_button.text
                vnal = get_vnal(driver)
                add_new_element(page_dict, brand, article, title, volume, driver.current_url, price, vnal)
                print(volume_button.text, 'success')
        else:
            price = get_price(driver)
            volume = get_one_volume(driver)
            vnal = get_vnal(driver)
            article = get_article(driver)
            add_new_element(page_dict, brand, article, title, volume, item_block_href, price, vnal)
    else:
        price = get_price(driver)
        volume = get_one_volume(driver)
        vnal = get_vnal(driver)
        article = get_article(driver)
        add_new_element(page_dict, brand, article, title, volume, item_block_href, price, vnal)

def get_all_items(driver, items_counter):
    start_time = time.time()
    current_time = time.time()
    ctr = 1
    while current_time - start_time <= 100: #УВЕЛИЧИТЬ В ДВА РАЗА МИНИМУМ ПЕРЕД ОСНОВНЫМ ПРОГОНОМ!!!!
        # Выводим сообщение каждую секунду
        driver.execute_script('window.scrollBy(0, document.body.scrollHeight);')
        time.sleep(0.1)  # Пауза в одну секунду
        for i in range(25):
            ActionChains(driver).key_down(Keys.UP).perform()
            time.sleep(0.15)
        if ctr % 5 == 0:
            try:
                driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/section[6]/div/div/div[2]/button').click()
            except Exception:
                pass
        current_time = time.time()  # Обновляем текущее время
        ctr += 1
    driver.get_screenshot_as_file("screenshot.png")
    try:
        first_var = driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div[2]').find_elements(By.TAG_NAME, 'a')

        if len(first_var) == 0:
            return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/main/div[3]').find_elements(By.TAG_NAME, 'a')
        return first_var
    except Exception:
        try:
            return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/section[6]').find_elements(By.TAG_NAME, 'a')
        except Exception:
            return driver.find_element(By.XPATH, '//*[@id="__layout"]/div/div[2]/section[5]/div/div').find_elements(By.TAG_NAME, 'a')
        
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

def parse(category):
    #---
    options = ChromeOptions()

    #---
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(1.5)
    driver.delete_all_cookies()
    delete_cache(driver)

    url = f'https://goldapple.ru/brands/{category}'
    print(163)
    driver.set_window_size(1800, 900)
    counter = 1

    print(171)
    page_dict = initiate_dict(dict())
    driver.execute_script("document.body.style.zoom='100%'")
    time.sleep(2)
    press_grid(driver)
    time.sleep(2)
    press_cross(driver)
    print(179)
    time.sleep(4)
    items_counter = 0
    driver.get(url)
    all_items = get_all_items(driver, items_counter)
    print(len(all_items))

    all_items_hrefs = list([i.get_attribute('href') for i in all_items if i.get_attribute('href') is not None])
    all_hrefs_right = []
    for href in all_items_hrefs:
        stri = href.split('//')[1]
        print(len(stri.split('/')), stri.split('/'))
        if len(stri.split('/')) == 2:
            all_hrefs_right.append(href)

    print(len(all_hrefs_right))

    for item_block_href in all_hrefs_right:
        driver.get(item_block_href)
        driver.execute_script("document.body.style.zoom='25%'")
        time.sleep(0.3)
        page_counter = 0
        for i in range(10):
            try:
                parse_product(driver, page_dict, item_block_href)
                break
            except Exception:
                page_counter += 1
                time.sleep(1)
        if page_counter == 40:
            print("Проблема, не получилось спарсить", item_block_href)
        print(page_counter, item_block_href)
        pd.DataFrame(page_dict).to_excel(fr'C:/Users/admin/PycharmProjects/pythonProject/price_parsers/parsers_output/golden_apple/{category}_{counter}.xlsx')
    delete_cache(driver)
    driver.close()
