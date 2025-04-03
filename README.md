# Схемы работы системы

## 1. Общая архитектура системы

```
+-------------------+       +-------------------+       +-------------------+
| Airflow Scheduler | ----> | Airflow Webserver | ----> | Dashboard (Dash)  |
| (DAG executions)  |       | (UI: localhost:8080) |    | (localhost:8050)  |
+-------------------+       +-------------------+       +-------------------+
          |                        |                        |
          v                        v                        v
+-------------------+       +-------------------+       +-------------------+
| PostgreSQL        | <---- | Parsing Tasks     | ----> | Analytics Storage |
| (Analytics DB)    |       | (Parsers)         |       | (Stats & Trends)  |
+-------------------+       +-------------------+       +-------------------+
          ^                        |
          |                        v
+-------------------+       +-------------------+
| SQL Server        | <---- | Google Sheets     |
| (datahouse)      |       | (Data Export)     |
+-------------------+       +-------------------+
```

- **Airflow Scheduler**: Управляет выполнением DAG'ов
- **Airflow Webserver**: UI для мониторинга
- **Dashboard**: Визуализация аналитики
- **Parsing Tasks**: Парсинг площадок
- **PostgreSQL**: Хранение аналитики
- **SQL Server**: Исходные данные
- **Google Sheets**: Экспорт результатов

## 2. DAG "full_price_parsing" - Полный цикл парсинга

```
+-----------------+
| clean_main_folder|
| (BashOperator)   |
+-----------------+
          |
          v
+-----------------+-----------------+-----------------+-----------------+-----------------+
| parse_wildberries| parse_ozon     | parse_gallery   | parse_golden_apple| parse_bt        |
| (PythonOperator) | (PythonOperator)| (PythonOperator)| (PythonOperator) | (PythonOperator)|
+-----------------+-----------------+-----------------+-----------------+-----------------+
          |                        |                        |                        |
          v                        v                        v                        v
+-----------------+       +-------------------+       +-------------------+
| process_parsed_data     | Analytics Storage | <---- | collect_stats     |
| (PythonOperator)        | (PostgreSQL)      |       | (Function)        |
+-----------------+       +-------------------+       +-------------------+
          |
          v
+-----------------+
| upload_to_gsheets|
| (PythonOperator) |
+-----------------+
          |
          v
+-----------------+
| Google Sheets    |
+-----------------+
```

- Запускается ежедневно
- Параллельный парсинг всех площадок
- Сбор статистики
- Обработка и экспорт данных

## 3. Поток данных аналитики

```
+-----------------+
| Parsing Task    |
| (Any platform)  |
+-----------------+
          |
          v
+-----------------+
| collect_stats   |
| - Items parsed  |
| - Errors count  |
| - Execution time|
| - Avg price     |
| - Discounts     |
+-----------------+
          |
          v
+-----------------+-----------------+
| parsing_stats   | price_trends    |
| (Table)         | (Table)         |
| - timestamp     | - timestamp     |
| - platform      | - platform      |
| - items_parsed  | - article       |
| - errors_count  | - price         |
| - execution_time| - discounted_price|
| - avg_price     | - in_stock      |
| - discount_%    |                 |
+-----------------+-----------------+
          |
          v
+-----------------+
| Dashboard       |
| - Items by platform|
| - Price trends  |
| - Errors by platform|
+-----------------+
```

- Сбор метрик с каждого парсинга
- Хранение в PostgreSQL
- Визуализация в Dash
