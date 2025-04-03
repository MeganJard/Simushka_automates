
import dash
from dash import dcc, html
import plotly.express as px
from analytics import analyze_history
import pandas as pd

app = dash.Dash(__name__)

def update_dashboard():
    stats_df, trends_df = analyze_history()
    
    # График количества спарсенных товаров по платформам
    fig_items = px.bar(stats_df.groupby('platform')['items_parsed'].sum().reset_index(),
                      x='platform', y='items_parsed', title='Items Parsed by Platform')
    
    # График средней цены по времени
    fig_price = px.line(trends_df.groupby(['timestamp', 'platform'])['price'].mean().reset_index(),
                       x='timestamp', y='price', color='platform', title='Average Price Trend')
    
    # График ошибок
    fig_errors = px.bar(stats_df.groupby('platform')['errors_count'].sum().reset_index(),
                       x='platform', y='errors_count', title='Errors by Platform')
    
    return html.Div([
        html.H1('Price Parsing Dashboard'),
        dcc.Graph(figure=fig_items),
        dcc.Graph(figure=fig_price),
        dcc.Graph(figure=fig_errors),
        dcc.Interval(id='interval-component', interval=300*1000, n_intervals=0)  # Обновление каждые 5 минут
    ])

app.layout = update_dashboard

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
