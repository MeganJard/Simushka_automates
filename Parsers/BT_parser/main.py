import pandas as pd
import os
from datetime import datetime
from .item_parser import parse
import sql_con

PLOSH = 'ibt.ru'

import telebot
def send_message_to_user(message):
    TOKEN = '7241309695:AAGblw7UNVejMafbtftgEl97lRq5zKWj2SE'
    USER_ID = '467688891'
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(USER_ID, message)

def bt_parser(only_checked=False):
    if only_checked == False:
        plytix_prods = pd.read_sql_query("""
            SELECT
                [Артикул],
                [Наименование], 
                [Brand]
            FROM [datahouse].[dbo].[View_Price1C_Auto]""", sql_con.engine_for_upload())
        rhm_prods = pd.read_sql_query("""
        SELECT [sku]
            ,[label]
            ,[brand]
        FROM [datahouse].[dbo].[plytix_products]""", sql_con.engine_for_upload())
        rhm_prods.columns = ['Артикул'] + list(rhm_prods.columns[1:])
        merged_data = pd.merge(rhm_prods, plytix_prods, on='Артикул', how='inner')
        merged_data.drop_duplicates(subset='Артикул', inplace=True)
        merged_data.drop('Brand', axis=1, inplace=True)
        merged_data.drop('label', axis=1, inplace=True)
        merged_data = merged_data.reset_index(drop=True)

        counter = 0
        for item in merged_data["Наименование"]:
            errors_counter = 0
            while True:
                try:
                    parse(item, clear=counter % 200 == 0)
                    break
                except Exception as e:
                    errors_counter += 1
                    if errors_counter >= 1:
                        break

                            
            counter += 1
            if counter % 50 == 0:
                send_message_to_user(f'{PLOSH} выполнено {counter} итераций')
    else:
        urls_and_name = pd.read_sql(f"""
            SELECT distinct [Ссылка на товар], [Название товара наше] 
            FROM [datahouse].[dbo].[wella_browser_search]
            WHERE ([Плохой артикул(1-да, пусто - нет)] = 0 OR [Плохой артикул(1-да, пусто - нет)] IS NULL)
            AND [Площадка] = '{PLOSH}'
            AND [Проверено] = 1
            """, sql_con.c())
        for index, row in urls_and_name.iterrows():
            parse(row['Название товара наше'], clear= index % 100, url=row['Ссылка на товар'])

if __name__ == '__main__':
    bt_parser(only_checked=True)