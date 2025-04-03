import pandas as pd
import sqlalchemy
from datetime import datetime
import os

def get_postgres_engine():
    return sqlalchemy.create_engine(
        f"postgresql://analytics:analytics_pass@postgres:5432/price_analytics"
    )

def init_analytics_db():
    engine = get_postgres_engine()
    with engine.connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS parsing_stats (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                platform VARCHAR(50),
                items_parsed INTEGER,
                errors_count INTEGER,
                execution_time FLOAT,
                avg_price FLOAT,
                discount_percentage FLOAT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS price_trends (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP,
                platform VARCHAR(50),
                article VARCHAR(100),
                price FLOAT,
                discounted_price FLOAT,
                in_stock BOOLEAN
            )
        """)

def collect_stats(platform, data_df, execution_time, errors_count=0):
    engine = get_postgres_engine()
    
    # Базовые статистики
    items_parsed = len(data_df)
    avg_price = data_df['Цена'].mean() if not data_df['Цена'].empty else 0
    discount_percentage = ((data_df['Цена'] - data_df['Цена со скидкой']) / data_df['Цена'] * 100).mean() if not data_df['Цена'].empty else 0

    stats_df = pd.DataFrame({
        'timestamp': [datetime.now()],
        'platform': [platform],
        'items_parsed': [items_parsed],
        'errors_count': [errors_count],
        'execution_time': [execution_time],
        'avg_price': [avg_price],
        'discount_percentage': [discount_percentage]
    })
    
    # Тренды цен
    trends_df = data_df[['Площадка', 'Артикул площадки', 'Цена', 'Цена со скидкой', 'Есть в наличии']].copy()
    trends_df['timestamp'] = datetime.now()
    trends_df.columns = ['platform', 'article', 'price', 'discounted_price', 'in_stock', 'timestamp']
    
    with engine.connect() as conn:
        stats_df.to_sql('parsing_stats', conn, if_exists='append', index=False)
        trends_df.to_sql('price_trends', conn, if_exists='append', index=False)

def analyze_history():
    engine = get_postgres_engine()
    stats_df = pd.read_sql("SELECT * FROM parsing_stats", engine)
    trends_df = pd.read_sql("SELECT * FROM price_trends", engine)
    return stats_df, trends_df
