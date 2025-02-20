import pandas as pd
import os
from datetime import datetime
from .item_parser_playwright import parse
import sql_con



PLOSH = 'wildberries.ru'
import telebot
def send_message_to_user(message):
    TOKEN = '7241309695:AAGblw7UNVejMafbtftgEl97lRq5zKWj2SE'
    USER_ID = '467688891'
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(USER_ID, message)

def wb_parser():
    counter = 0
    searched_data = pd.read_excel('./YANDEX_SEARCH_RESULTS.xlsx')
    for index, item in searched_data[searched_data['plosh'] == PLOSH][['Наименование', 'operation_id']].iterrows():
        errors_counter = 0
        try:
            parse(item['Наименование'], item['operation_id'])
            
        except Exception as e:
            send_message_to_user(f'ERRRRRRRRRRROR WILDBERRIES {e}')
            pass




if __name__ == '__main__':
    wb_parser()
