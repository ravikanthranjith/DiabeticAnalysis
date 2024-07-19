import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import os

# Define the file path
file_path = os.path.join(os.path.dirname(__file__), 'Ravikanth_Narayanabhatla_ZivovGlucoseData.xlsx')

# Load the data
try:
    glucose_data = pd.read_excel(file_path)
    glucose_data['Time'] = pd.to_datetime(glucose_data['Time'], format='%b %d %Y, %I:%M %p')
except Exception as e:
    print(f"Error loading data: {e}")
    glucose_data = pd.DataFrame()  # Create an empty DataFrame in case of error

# Create the Dash app
app = dash.Dash(__name__)
server = app.server  # Define the server for deployment

app.layout = html.Div([
    html.H1("Glucose Insights"),
    html.Div([
        html.H3("Summary Statistics"),
        html.Ul(id='summary-stats')
    ]),
    html.Div([
        html.Label('Select X-axis:'),
        dcc.Dropdown(
            id='xaxis-column',
            options=[{'label': 'Time', 'value': 'Time'}, {'label': 'Glucose Value', 'value': 'Glucose Value'}],
            value='Time'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Select Y-axis:'),
        dcc.Dropdown(
            id='yaxis-column',
            options=[{'label': 'Time', 'value': 'Time'}, {'label': 'Glucose Value', 'value': 'Glucose Value'}],
            value='Glucose Value'
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
        html.Label('Filter Glucose Values:'),
        dcc.RangeSlider(
            id='glucose-filter',
            min=0,
            max=glucose_data['Glucose Value'].max(),
            step=1,
            value=[glucose_data['Glucose Value'].min(), glucose_data['Glucose Value'].max()],
            marks={int(i): str(int(i)) for i in range(int(glucose_data['Glucose Value'].min()), int(glucose_data['Glucose Value'].max())+1, 10)}
        ),
    ], style={'width': '98%', 'padding': '20px'}),
    html.Div([
        html.Label('Filter Time Range:'),
        dcc.DatePickerRange(
            id='time-filter',
            start_date=glucose_data['Time'].min().date(),
            end_date=glucose_data['Time'].max().date(),
            display_format='YYYY-MM-DD'
        ),
    ], style={'width': '98%', 'padding': '20px'}),
    dcc.Graph(id='glucose-graph')
])

@app.callback(
    [Output('glucose-graph', 'figure'), Output('summary-stats', 'children')],
    [Input('xaxis-column', 'value'),
     Input('yaxis-column', 'value'),
     Input('glucose-filter', 'value'),
     Input('time-filter', 'start_date'),
     Input('time-filter', 'end_date')]
)
def update_graph(xaxis_column_name, yaxis_column_name, glucose_filter_range, start_date, end_date):
    if glucose_data.empty:
        return {}, ["Error loading data"]

    if start_date is None:
        start_date = glucose_data['Time'].min()
    else:
        start_date = pd.to_datetime(start_date)

    if end_date is None:
        end_date = glucose_data['Time'].max()
    else:
        end_date = pd.to_datetime(end_date)

    filtered_data = glucose_data[
        (glucose_data['Glucose Value'] >= glucose_filter_range[0]) & 
        (glucose_data['Glucose Value'] <= glucose_filter_range[1]) &
        (glucose_data['Time'] >= start_date) & 
        (glucose_data['Time'] <= end_date)
    ]
    fig = px.line(filtered_data, x=xaxis_column_name, y=yaxis_column_name, title='Glucose Levels')
    fig.update_layout(transition_duration=500)
    summary_stats = [
        html.Li(f"Minimum Glucose Level: {filtered_data['Glucose Value'].min()} mg/dL"),
        html.Li(f"Maximum Glucose Level: {filtered_data['Glucose Value'].max()} mg/dL"),
        html.Li(f"Average Glucose Level: {filtered_data['Glucose Value'].mean():.2f} mg/dL"),
        html.Li(f"Hypoglycemia Count: {(filtered_data['Glucose Value'] < 70).sum()}"),
        html.Li(f"Hyperglycemia Count: {(filtered_data['Glucose Value'] > 180).sum()}")
    ]
    return fig, summary_stats

if __name__ == '__main__':
    app.run_server(debug=False)
