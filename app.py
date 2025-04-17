
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import calendar

pga_data = pd.read_csv("/content/ASA All PGA Raw Data - Tourn Level.csv")

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.title = "2022 Year-end Top 10 Monthly Performance"

year_2022_end_rankings = ['Scottie Scheffler', 'Rory McIlroy', 'Cameron Smith', 'Patrick Cantlay', 'Xander Schauffele', 'Jon Rahm', 'Justin Thomas', 'Will Zalatoris', 'Collin Morikawa', 'Viktor Hovland']

pga_2022 = pga_data[(pga_data['season'] == 2022) & (pga_data['player'].isin(year_2022_end_rankings))]

pga_2022 = pga_2022.dropna(subset=['sg_ott', 'sg_app', 'sg_arg', 'sg_putt'])

pga_2022['month'] = pd.to_datetime(pga_2022['date']).dt.month

averages_by_month = (pga_2022.groupby(['month', 'player'])[['sg_ott', 'sg_app', 'sg_arg', 'sg_putt']].mean().reset_index())

metrics = {'sg_ott': 'Driving', 'sg_app': 'Approach', 'sg_arg': 'Chipping','sg_putt': 'Putting'}

reverse_metrics = {v: k for k, v in metrics.items()}

app.layout = html.Div([
    html.H1(
        "2022 Year-end Top 10 Monthly Performance",
        style = {'color': 'white', 'textAlign': 'center'}
    ),

    html.Label("Select Performance Metric:", style = {'color': 'white'}),
    dcc.Dropdown(
        id ='metric_dropdown',
        options = [{'label': v, 'value': v} for v in metrics.values()],
        value = 'Driving'
    ),

    html.Br(),
    html.Label("Select Month:", style = {'color': 'white'}),
    dcc.Slider(
    id = 'month_slider',
    min = 1,
    max = 12,
    step = 1,
    marks = {i: calendar.month_name[i] for i in range(1, 13)},
    value = 1,
    tooltip = {"always_visible": False}
),

    html.Br(),
    html.Label("Select Players:", style = {'color': 'white'}),
    dcc.Dropdown(
        id = 'player_filter',
        options = [{'label': p, 'value': p} for p in year_2022_end_rankings],
        value = year_2022_end_rankings,
        multi = True
    ),

    html.Br(),
    dcc.Graph(id = 'bar_chart')
], style = {
    'backgroundColor': '#1e1e1e',
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})

@app.callback(
    Output('bar_chart', 'figure'),
    Input('metric_dropdown', 'value'),
    Input('month_slider', 'value'),
    Input('player_filter', 'value')
)
def update_chart(selected_metric_label, selected_month, selected_players):
    metric_col = reverse_metrics[selected_metric_label]
    month_name = calendar.month_name[selected_month]

    filtered = averages_by_month[
        (averages_by_month['month'] == selected_month) &
        (averages_by_month['player'].isin(selected_players))
    ].copy()

    rory_na = False
    if 'Rory McIlroy' in selected_players and 'Rory McIlroy' not in filtered['player'].values:
        rory_row = {
            'month': selected_month,
            'player': 'Rory McIlroy',
            'sg_ott': 0,
            'sg_app': 0,
            'sg_arg': 0,
            'sg_putt': 0,
            'note': 'No Data'
        }
        filtered = pd.concat([filtered, pd.DataFrame([rory_row])], ignore_index=True)
        rory_na = True

    fig = px.bar(
        filtered.sort_values(by = metric_col, ascending = False),
        x = 'player',
        y = metric_col,
        color = metric_col,
        color_continuous_scale=[
            '#d73027', '#f46d43', '#fefefe', '#1a9850', '#006837'
        ],
        color_continuous_midpoint = 0,
        title = f"{selected_metric_label} in {month_name} 2022 for Top 10 Players",
        labels = {metric_col: 'Average Strokes Gained', 'player': 'Player'}
    )

    if rory_na:
        fig.add_annotation(
            x = 'Rory McIlroy',
            y = 0,
            text = "No Data",
            showarrow = False,
            font = dict(color="gray", size=12),
            yshift = 10
        )

    fig.update_layout(
        xaxis_tickangle = -45,
        coloraxis_showscale = False,
        paper_bgcolor = '#2b2b2b',
        plot_bgcolor = '#2b2b2b',
        font_color = 'white',
        font = dict(size = 14)
    )

    return fig

if __name__ == '__main__':
    app.run(debug = True)
