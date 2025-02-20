import concurrent.futures
import pygsheets
from wb_parser.main import wb_parser
from ozon_parser.main import ozon_parser
from gallery_parser.main import gallery_parser
from golden_apple_parser.main import ga_parser
from BT_parser.main import bt_parser
import pandas as pd
import os
import pyodbc
import sqlalchemy
from datetime import datetime
import shutil
import telebot
from ml_model_class import DistilBERTClassifier

SERVER = "10.10.10.26"
DATABASE = "datahouse"
USERNAME = "bogdanov"
PASSWORD = "hLa4m95S"

def write_to_gsheet(service_file_path, spreadsheet_id, sheet_name, data_df):
      # Авторизация
    gc = pygsheets.authorize(service_file=service_file_path)
    
    # Открытие таблицы по ID
    sh = gc.open_by_key(spreadsheet_id)
    
    # Проверка существования листа
    try:
        wks_write = sh.worksheet_by_title(sheet_name)
    except pygsheets.WorksheetNotFound:
        # Если лист не найден, создаем новый
        wks_write = sh.add_worksheet(sheet_name)

    # Очистка данных начиная с ячейки A2 (если необходимо)
    wks_write.clear('A1', end=None)
    wks_write.set_dataframe(data_df, (1,1), encoding='utf-8', fit=True)
    # wks_write.frozen_rows = 1

# Функция для вычитания 2000 лет с использованием datetime
# Функция для вычитания 2000 лет из даты в виде строки
def subtract_years(date_str, years):
    # Извлекаем только часть даты (год-месяц-день)
    date_part = date_str.split(' ')[0]
    year, month, day = map(int, date_part.split('-'))
    new_year = year - years
    return f"{new_year:04d}-{month:02d}-{day:02d}"

def send_message_to_user(message):
    TOKEN = '7241309695:AAGblw7UNVejMafbtftgEl97lRq5zKWj2SE'
    USER_ID = '467688891'
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(USER_ID, message)

def delete_all_contents(folder_path):
    try:
        # Проверяем, существует ли папка
        if not os.path.exists(folder_path):
            print(f"Папка {folder_path} не существует.")
            return
        
        # Перебираем все файлы и папки в указанной директории
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            try:
                # Если это файл или символическая ссылка, удаляем его
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                # Если это директория, удаляем её и всё её содержимое
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except Exception as e:
                print(f"Не удалось удалить {item_path}. Причина: {e}")
        
        print(f"Все файлы и папки в {folder_path} успешно удалены.")
    
    except Exception as e:
        print(f"Произошла ошибка: {e}")



def cur():
    sql_connection = pyodbc.connect(r'Driver=ODBC Driver 17 for SQL Server;Server='+SERVER+';Database='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
    return sql_connection

def engine_for_upload():
    engine = sqlalchemy.create_engine(
            "mssql+pyodbc://bogdanov:hLa4m95S@10.10.10.26/datahouse?driver=ODBC Driver 17 for SQL Server",
            echo=False)
    print('engine_created')
    return engine

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
    page_dict['Наше название'] = []
    return page_dict

def final_func():
    plytix_prods = pd.read_sql_query("""
    SELECT
        [Артикул],
        [Наименование], 
        [Brand]
    FROM [datahouse].[dbo].[View_Price1C_Auto]""", cur())
    rhm_prods = pd.read_sql_query("""
    SELECT [sku]
        ,[label]
        ,[brand]
    FROM [datahouse].[dbo].[plytix_products]""", cur())
    rhm_prods.columns = ['Артикул'] + list(rhm_prods.columns[1:])
    merged_data = pd.merge(rhm_prods, plytix_prods, on='Артикул', how='inner')
    merged_data.drop_duplicates(subset='Артикул', inplace=True)
    merged_data.drop('Brand', axis=1, inplace=True)
    merged_data.drop('label', axis=1, inplace=True)
    merged_data = merged_data.reset_index(drop=True)


    path_to_dir = r'C:/Users/admin/PycharmProjects/pythonProject/price_parsers/main_folder/'
    all_files = os.listdir(path_to_dir)
    error_counter = 0
    data = pd.DataFrame(initiate_dict({}))
    for index, filename in enumerate(all_files):
        try: 
            data = pd.concat([data, pd.read_excel(path_to_dir+filename)])
        except Exception as e:
            error_counter += 1

    merged_data.columns = list(merged_data.columns)[:-1]+['Название товара наше']

    data = data.applymap(lambda x: x.replace('\u2009', '') if isinstance(x, str) else x)

    data['Цена'] = [float(str(cell_val).replace('₽', '').replace(' ', '').replace('\xa0', '')) if cell_val is not None else None for cell_val in
                    data['Цена']]
    data['Цена со скидкой'] = [float(str(cell_val).replace('₽', '').replace(' ', '').replace('\xa0', '')) if not pd.isna(cell_val) else None for
                            cell_val in data['Цена со скидкой']]
    
    data['Название товара на площадке'] = data['Название товара на площадке'].fillna(data['Название товара'])
    data['Название товара наше'] = data['Название товара наше'].fillna(data['Наше название'])
    new_data = pd.merge(data, merged_data, on='Название товара наше', how='inner')
    new_data.columns = list(new_data.columns[:15]) + ['Артикул наш'] + list(new_data.columns[16:])


    model_path = 'distilbert_model.pth'  # Путь к сохраненной модели
    classifier = DistilBERTClassifier(model_path)
    new_data = new_data[['Название товара на площадке', 'Название товара наше',
        'Ссылка на товар', 'Бренд',
        'Площадка', 'Артикул площадки', 'Объем', 'Цена', 'Цена со скидкой',
        'Есть в наличии', 'Дата парсинга', 'Артикул наш']]
    new_data['Проверено'] = 0
  # answer = classifier.predict(new_data['Название товара на площадке'] + " " + new_data['Название товара наше']) #!!!
    new_data['Плохой артикул(1-да, пусто - нет)'] = 0
    
    new_data['Артикул площадки'] = new_data['Артикул площадки'].astype(str)
    new_data['Артикул площадки'] = new_data['Артикул площадки'].str.replace(' ', '')
    new_data['upload_date'] = datetime.now().strftime('%Y-%m-%d')

    
    new_data.to_sql('wella_browser_search', engine_for_upload(), index=False, if_exists='append')
    
    new_data.to_excel('checker.xlsx')
#     conn = cur()
#     cursor = conn.cursor()
#     cursor.execute(f"""
#         UPDATE t1
#         SET [Плохой артикул(1-да, пусто - нет)] = 1
#         FROM wella_browser_search t1
#         WHERE upload_date = '{datetime.now().strftime('%Y-%m-%d')}'
#             AND EXISTS (
#                 SELECT 1
#                 FROM wella_browser_search t2
#                 WHERE t1.[Артикул площадки] = t2.[Артикул площадки]
#                 AND t1.[Артикул наш] = t2.[Артикул наш]
#                 AND t2.[Плохой артикул(1-да, пусто - нет)] = 1
#             );
# """)
#     conn.commit()
#     conn.close()
#     pd.read_sql_query(f"""SELECT
#        [Название товара на площадке]
#       ,[Название товара наше]
#       ,[Ссылка на товар]
#       ,[Бренд]
#       ,[Плохой артикул(1-да, пусто - нет)]
#       ,[Площадка]
#       ,[Артикул площадки]
#       ,[Объем]
#       ,[Цена]
#       ,[Цена со скидкой]
#       ,[Есть в наличии]
#       ,[Дата парсинга]
#       ,[Артикул наш]
#       ,[Проверено]
#       ,[upload_date] from wella_browser_search where upload_date = '{datetime.now().strftime('%Y-%m-%d')}' """, cur()).to_excel(fr'C:\Users\admin\PycharmProjects\pythonProject\price_parsers\history\{datetime.now().strftime("%Y-%m-%d")}.xlsx', index=False)

def collect_and_move_to_gsheets():
    parsed_data = pd.read_sql_query("""
        SELECT
            *                                              
        FROM [datahouse].[dbo].[wella_browser_search]""", cur())
    parsed_data['Дата парсинга'] = pd.to_datetime(parsed_data['Дата парсинга'])
    parsed_data.sort_values(by=['Артикул наш', "Площадка",'Дата парсинга'], inplace=True)

    plytix_prods = pd.read_sql_query("""
        SELECT
            [Артикул],
            [Наименование], 
            [Brand], 
            [Цена],
            [_Period],
            [Наименование типа цен]                                                
        FROM [datahouse].[dbo].[View_Price1C_Auto]""", cur())
    rhm_prods = pd.read_sql_query("""
    SELECT [sku]
        ,[label]
        ,[brand]
        ,[family]
        ,[categories]
        ,[line]
        ,[subline]                        
                                                                                
    FROM [datahouse].[dbo].[plytix_products]""", cur())
    rhm_prods.columns = ['Артикул'] + list(rhm_prods.columns[1:])
    merged_data = pd.merge(rhm_prods, plytix_prods, on='Артикул', how='inner')
    merged_data.drop('Brand', axis=1, inplace=True)
    merged_data.drop('label', axis=1, inplace=True)
    merged_data = merged_data.reset_index(drop=True)
    merged_data['_Period'] = merged_data['_Period'].astype(str)


    # Применение функции к столбцу
    merged_data['_Period'] = merged_data['_Period'].apply(lambda x: subtract_years(x, 2000))

    write_to_gsheet('rhm-prices-control-1776575457d7.json', '14ewOLwmtWxn3Ne9kOlXnnZ5wsECQqiWzLKhs8s3Bdl0', 'Parsed_data', parsed_data)
    write_to_gsheet('rhm-prices-control-1776575457d7.json', '19JxGeJGAiGPXSLuhl09vx-FUa5UvrUXtEhE0nfxnGfM', 'Our_data', merged_data)

# while True:
#delete_all_contents(r'C:\Users\admin\PycharmProjects\pythonProject\price_parsers\main_folder')
# # Запуск параллельных задач
    # Ожидание завершения оставшихся двух задач

# import concurrent.futures

# with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
#     # Создаем список всех задач
#     all_tasks = [
#         executor.submit(ga_parser),
#        # executor.submit(bt_parser, [False]),
#         executor.submit(wb_parser),
#         executor.submit(ozon_parser),
#         executor.submit(gallery_parser)
#     ]
    
#     # Ожидание завершения всех задач
#     for future in concurrent.futures.as_completed(all_tasks):
#         try:
#             # Получаем результат задачи (если нужно)
#             result = future.result()
#         except Exception as e:
#             # Логируем ошибку, если она возникла
#             send_message_to_user(f"Трындец. Ошибка в задаче: {e}")

final_func()

#collect_and_move_to_gsheets()