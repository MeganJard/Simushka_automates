# Документация скрипта парсинга товаров на примере proficosmetics.ru
Пусть у нас есть n площадок. Парсер каждой из них представляет из себя связку единичная функция + main, который занимается сбором данных из бд, которые будем парсить. Далее все main файлы от всех площадок собираются в один большой во внешней директории

## Описание единичной функции
Скрипт предназначен для парсинга информации о товарах с сайта proficosmetics.ru. Использует Playwright для автоматизации браузера и извлечения данных о товарах, сохраняя результаты в Excel-файл.

## Зависимости
- `time` - для временных задержек
- `pandas` - для работы с данными и сохранения в Excel
- `datetime` - для работы с датами
- `re` - для обработки строк с помощью регулярных выражений
- `playwright.sync_api` - для автоматизации браузера
- `xml.etree.ElementTree` - для парсинга XML-файлов

## Глобальные переменные
- `PLOSHADKA = 'proficosmetics.ru'` - константа с названием площадки

## Функции

### `get_plosh()`
- **Описание**: Возвращает название площадки
- **Возвращает**: string - `'proficosmetics.ru'`

### `initiate_dict(page_dict)`
- **Описание**: Инициализирует словарь для хранения данных о товарах
- **Параметры**: 
  - `page_dict` (dict) - пустой словарь
- **Возвращает**: dict - словарь с пустыми списками по следующим ключам:
  - Площадка
  - Бренд
  - Артикул площадки
  - Название товара на площадке
  - Объем
  - Ссылка на товар
  - Цена
  - Цена со скидкой
  - Есть в наличии
  - Дата парсинга
  - Кол-во в наличии
  - Название товара наше

### `add_new_element(page_dict, brand, article, title, volume_1, item_block_href, price, vnal, our_name)`
- **Описание**: Добавляет данные о товаре в словарь
- **Параметры**:
  - `page_dict` (dict) - словарь для хранения данных
  - `brand` (str) - название бренда
  - `article` (str) - артикул товара
  - `title` (str) - название товара на площадке
  - `volume_1` (str) - объем товара
  - `item_block_href` (str) - ссылка на товар
  - `price` (list) - список цен [старая цена, новая цена]
  - `vnal` (bool) - наличие товара
  - `our_name` (str) - наше название товара
- **Логика**:
  - Очищает цены от символов ₽, пробелов и других лишних символов
  - Сортирует цены (большая - обычная, меньшая - со скидкой)
  - Добавляет данные в соответствующие списки словаря

### `get_brand_name(page)`
- **Описание**: Извлекает название бренда со страницы
- **Параметры**: 
  - `page` - объект страницы Playwright
- **Возвращает**: str - название бренда

### `get_article(page)`
- **Описание**: Извлекает артикул товара
- **Параметры**: 
  - `page` - объект страницы Playwright
- **Возвращает**: str - артикул после двоеточия в блоке `.kr_product_info p`

### `get_clear_name_and_vol(page)`
- **Описание**: Извлекает чистое название товара и объем
- **Параметры**: 
  - `page` - объект страницы Playwright
- **Возвращает**: tuple - (название товара без объема, объем или None)

### `get_price(page)`
- **Описание**: Извлекает старую и новую цену товара
- **Параметры**: 
  - `page` - объект страницы Playwright
- **Возвращает**: tuple - (старая цена или пустая строка, новая цена)

### `relog(page)`
- **Описание**: Выполняет авторизацию на сайте
- **Параметры**: 
  - `page` - объект страницы Playwright
- **Действия**:
  - Переходит на страницу авторизации
  - Заполняет поля логина и пароля
  - Нажимает кнопку входа

### `xml_unpack(operation_id)`
- **Описание**: Извлекает URL из XML-файла
- **Параметры**: 
  - `operation_id` (str) - идентификатор операции для поиска файла
- **Возвращает**: list - список URL из тегов `<url>` в XML

### `parse(item, operation_id)`
- **Описание**: Основная функция парсинга страницы товара
- **Параметры**: 
  - `item` (str) - наше название товара
  - `operation_id` (str/bool) - идентификатор операции или False
- **Логика**:
  - Запускает браузер Chromium в видимом режиме
  - Извлекает URL из XML (если указан operation_id)
  - Выполняет авторизацию
  - Парсит страницу товара
  - Сохраняет данные в Excel-файл
- **Вывод**: Excel-файл в папке `main_folder` с именем `gallery_[item].xlsx`

## Документация скрипта парсинга галереи товаров (gallery_parser)

### Описание
Скрипт предназначен для массового парсинга товаров с сайта `proficosmetics.ru` на основе данных из Excel-файла `YANDEX_SEARCH_RESULTS.xlsx`. Использует функцию `parse` из модуля `item_parser_playwright` для обработки каждого товара и отправляет уведомления в Telegram в случае ошибок.

### Зависимости
- `pandas` - для работы с данными из Excel
- `item_parser_playwright` - пользовательский модуль с функцией `parse`
- `telebot` - для отправки сообщений в Telegram

### Глобальные переменные
- `PLOSH = 'proficosmetics.ru'` - константа с названием площадки

### Функции

#### `send_message_to_user(message)`
- **Описание**: Отправляет сообщение пользователю в Telegram
- **Параметры**: 
  - `message` (str) - текст сообщения
- **Константы**:
  - `TOKEN` (str) - токен Telegram-бота: ``
  - `USER_ID` (str) - идентификатор пользователя: ``
- **Логика**:
  - Создает объект бота с указанным токеном
  - Отправляет сообщение указанному пользователю

#### `gallery_parser()`
- **Описание**: Основная функция для парсинга товаров из галереи
- **Логика**:
  1. Читает данные из файла `./YANDEX_SEARCH_RESULTS.xlsx` в DataFrame
  2. Фильтрует строки, где значение столбца `plosh` равно `PLOSH` (`proficosmetics.ru`)
  3. Итерируется по отфильтрованным строкам, извлекая `Наименование` и `operation_id`
  4. Для каждого товара вызывает функцию `parse` с параметрами `Наименование` и `operation_id`
  5. Обрабатывает исключения:
     - При ошибке отправляет сообщение в Telegram с текстом `ERRRRRRRRRRROR GALLERY {ошибка}`

### Основной запуск
```python
if __name__ == '__main__':
    gallery_parser()
```
# Документация скрипта интеграции парсинга данных

## Описание
Скрипт предназначен для параллельного парсинга данных с различных торговых площадок, их обработки, интеграции с данными из SQL Server и загрузки в Google Sheets и SQL базу данных. Использует многопоточность для выполнения задач парсинга, модель машинного обучения для классификации и Telegram для уведомлений об ошибках.

## Зависимости
- `concurrent.futures` - для многопоточного выполнения
- `pygsheets` - для работы с Google Sheets
- `wb_parser.main`, `ozon_parser.main`, `gallery_parser.main`, `golden_apple_parser.main`, `BT_parser.main` - модули парсинга конкретных площадок
- `pandas` - для работы с данными
- `os`, `shutil` - для работы с файловой системой
- `pyodbc`, `sqlalchemy` - для подключения к SQL Server
- `datetime` - для работы с датами
- `telebot` - для отправки уведомлений в Telegram

## Глобальные переменные
- `SERVER` - адрес SQL сервера
- `DATABASE` - имя базы данных
- `USERNAME` - имя пользователя SQL
- `PASSWORD` - пароль пользователя SQL

## Функции

### `write_to_gsheet(service_file_path, spreadsheet_id, sheet_name, data_df)`
- **Описание**: Записывает DataFrame в Google Sheets
- **Параметры**:
  - `service_file_path` (str) - путь к файлу учетных данных Google
  - `spreadsheet_id` (str) - ID таблицы Google Sheets
  - `sheet_name` (str) - имя листа
  - `data_df` (DataFrame) - данные для записи
- **Логика**:
  - Авторизуется с помощью сервисного файла
  - Открывает таблицу, создает лист если его нет
  - Очищает лист и записывает данные

### `subtract_years(date_str, years)`
- **Описание**: Вычитает указанное количество лет из строки даты
- **Параметры**:
  - `date_str` (str) - строка даты в формате `YYYY-MM-DD ...`
  - `years` (int) - количество лет для вычитания
- **Возвращает**: str - новая дата в формате `YYYY-MM-DD`

### `send_message_to_user(message)`
- **Описание**: Отправляет сообщение в Telegram
- **Параметры**:
  - `message` (str) - текст сообщения
- **Константы**:
  - `TOKEN` - токен бота
  - `USER_ID` - ID пользователя
- **Логика**: Создает бота и отправляет сообщение

### `delete_all_contents(folder_path)`
- **Описание**: Удаляет все содержимое папки
- **Параметры**:
  - `folder_path` (str) - путь к папке
- **Логика**:
  - Удаляет файлы и подкаталоги
  - Обрабатывает ошибки и выводит сообщения

### `cur()`
- **Описание**: Создает подключение к SQL Server
- **Возвращает**: pyodbc.Connection - объект подключения

### `engine_for_upload()`
- **Описание**: Создает движок SQLAlchemy для загрузки данных
- **Возвращает**: sqlalchemy.Engine - движок базы данных

### `initiate_dict(page_dict)`
- **Описание**: Инициализирует словарь для данных о товарах
- **Параметры**:
  - `page_dict` (dict) - пустой словарь
- **Возвращает**: dict - словарь с ключами для данных товаров

### `final_func()`
- **Описание**: Основная функция обработки и интеграции данных
- **Логика**:
  1. Загружает данные из SQL (`View_Price1C_Auto` и `plytix_products`)
  2. Объединяет данные по артикулу
  3. Читает спарсенные данные из Excel-файлов в папке `main_folder`
  4. Обрабатывает цены и названия
  5. Объединяет с данными из SQL
  6. Применяет модель DistilBERT (закомментировано)
  7. Добавляет метки и дату загрузки
  8. Сохраняет в SQL таблицу `wella_browser_search` и Excel `checker.xlsx`
  9. (Закомментировано) Обновляет флаг "Плохой артикул" в SQL и сохраняет историю

### `collect_and_move_to_gsheets()`
- **Описание**: Собирает данные из SQL и загружает в Google Sheets
- **Логика**:
  1. Загружает данные из `wella_browser_search`
  2. Сортирует по артикулу, площадке и дате
  3. Загружает и объединяет данные из `View_Price1C_Auto` и `plytix_products`
  4. Корректирует даты (вычитает 2000 лет)
  5. Записывает в два Google Sheets: `Parsed_data` и `Our_data`

## Основной запуск
```python
final_func()
# collect_and_move_to_gsheets()
```
