import pygsheets
import pandas as pd
import sqlalchemy
import pyodbc


SERVER = "10.77.77.6"
DATABASE = "datahouse"
USERNAME = "bogdanov"
PASSWORD = "hLa4m95S"
def c():
    sql_connection = pyodbc.connect(r'Driver=ODBC Driver 17 for SQL Server;Server='+SERVER+';Database='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
    return sql_connection
def engine_for_upload():
    engine = sqlalchemy.create_engine(
               "mssql+pyodbc://bogdanov:hLa4m95S@10.77.77.6/datahouse?driver=ODBC Driver 17 for SQL Server",
               echo=False)
    return engine


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

parsed_data = pd.read_sql_query("""
    SELECT
        *                                              
    FROM [datahouse].[dbo].[wella_browser_search]""", engine_for_upload())
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
    FROM [datahouse].[dbo].[View_Price1C_Auto]""", engine_for_upload())
rhm_prods = pd.read_sql_query("""
   SELECT [sku]
      ,[label]
      ,[brand]
      ,[family]
      ,[categories]
      ,[line]
      ,[subline]                        
                                                                              
  FROM [datahouse].[dbo].[plytix_products]""", engine_for_upload())
rhm_prods.columns = ['Артикул'] + list(rhm_prods.columns[1:])
merged_data = pd.merge(rhm_prods, plytix_prods, on='Артикул', how='inner')
merged_data.drop('Brand', axis=1, inplace=True)
merged_data.drop('label', axis=1, inplace=True)
merged_data = merged_data.reset_index(drop=True)
merged_data['_Period'] = merged_data['_Period'].astype(str)

# Функция для вычитания 2000 лет с использованием datetime
# Функция для вычитания 2000 лет из даты в виде строки
def subtract_years(date_str, years):
    # Извлекаем только часть даты (год-месяц-день)
    date_part = date_str.split(' ')[0]
    year, month, day = map(int, date_part.split('-'))
    new_year = year - years
    return f"{new_year:04d}-{month:02d}-{day:02d}"

# Применение функции к столбцу
merged_data['_Period'] = merged_data['_Period'].apply(lambda x: subtract_years(x, 2000))

write_to_gsheet('rhm-prices-control-1776575457d7.json', '14ewOLwmtWxn3Ne9kOlXnnZ5wsECQqiWzLKhs8s3Bdl0', 'Parsed_data', parsed_data)
write_to_gsheet('rhm-prices-control-1776575457d7.json', '19JxGeJGAiGPXSLuhl09vx-FUa5UvrUXtEhE0nfxnGfM', 'Our_data', merged_data)
