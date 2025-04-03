# Simushka_automates

+-------------------+       +-------------------+       +-------------------+
| Airflow Scheduler | ----> | Airflow Webserver | ----> | Dashboard (Dash)  |
| (DAG execution)   |       | (UI: localhost:8080) |    | (localhost:8050)  |
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
