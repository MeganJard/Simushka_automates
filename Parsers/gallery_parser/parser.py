from selenium.webdriver.common.by import By
import time
from selenium import webdriver
import pandas as pd
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from datetime import datetime

PLOSHADKA = 'proficosmetics.ru'



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
    time.sleep(0.3)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(0.3)
    driver.get('chrome://settings/clearBrowserData') # for old chromedriver versions use cleardriverData
    time.sleep(0.3)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 1 + Keys.ENTER * 1) # send right combination
    actions.perform()
    time.sleep(0.3)
    driver.close() # close this tab
    driver.switch_to.window(driver.window_handles[0]) # switch back

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
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys('s666999s')
    driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div/div/div/form/button').click()

def reinit(driver):
    counter = 0
    while True:
        try:
            driver.close()
            time.sleep(100)
            driver = webdriver.Chrome()
            relog(driver)
            driver.execute_script("document.body.style.zoom='25%'")
            driver.set_window_size(1800, 900)
            driver.implicitly_wait(2)
            return driver
        except Exception:
            if counter == 5:
                raise Exception('ALL CRASHED')
            time.sleep(10)
            counter += 1




def parse(category):

    driver = webdriver.Chrome()

    driver.implicitly_wait(2)

    delete_cache(driver)
    while True:
        try:
            relog(driver)
            break
        except Exception:
            driver = reinit(driver)
            time.sleep(5)
    time.sleep(2)
    url = f'https://www.proficosmetics.ru/catalog/{category}/'
    driver.get(url)
    driver.set_window_size(1800, 900)
    driver.execute_script("document.body.style.zoom='25%'")

    while True:
        try:
            menu_buttons_footer = list(driver.find_elements(By.CLASS_NAME, 'pager'))[0]
            print('Menu_footer:',menu_buttons_footer)
            number_of_pages = int(menu_buttons_footer.text.split()[-2])
            print('number_of_pages:', number_of_pages)
            break
        except IndexError:

            number_of_pages = 1
            break
    page_dict = {}
    initiate_dict(page_dict)

    print('Number of pages:',number_of_pages)
    for page_index in range(1, number_of_pages+1):
        time.sleep(5)

        driver.get(url+f'p{page_index}')

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
                    driver.get(item_block_href)
                    if len(driver.find_elements(By.CLASS_NAME, 'kr_variants')):
                        all_vols_links = [block.get_attribute('href') for block in driver.find_elements(By.CLASS_NAME, 'kr_variants')[0].find_elements(By.TAG_NAME, 'a')]
                        for vol_link in all_vols_links:
                            driver.get(vol_link)
                            time.sleep(0.5)
                            link = vol_link
                            brand_name = get_brand_name(driver)
                            product_clear_name, volume = get_clear_name_and_vol(driver)
                            artikul = get_article(driver)
                            price = get_price(driver)
                            add_new_element(page_dict, brand_name, artikul, product_clear_name, volume, link, price, True)
                            pd.DataFrame(page_dict).to_excel(fr'C:\Users\admin\PycharmProjects\pythonProject\price_parsers\parsers_output\gallery_cosm\{category}.xlsx')
                    else:
                        time.sleep(0.5)
                        link = item_block_href
                        brand_name = get_brand_name(driver)
                        product_clear_name, volume = get_clear_name_and_vol(driver)
                        artikul = get_article(driver)
                        price = get_price(driver)
                        add_new_element(page_dict, brand_name, artikul, product_clear_name, volume, link, price, True)
                        pd.DataFrame(page_dict).to_excel(fr'C:\Users\admin\PycharmProjects\pythonProject\price_parsers\parsers_output\gallery_cosm\{category}.xlsx')
                    break
                except Exception:
                    print('CAPTCHA DETECTED')
                    if captcha_counter == 2:
                        captcha_counter = 0
                        break
                    captcha_counter += 1
                    driver = reinit(driver)
    driver.close()

