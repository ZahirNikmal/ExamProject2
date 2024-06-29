from dash import Dash, html, dcc
from dash.dependencies import Input, Output, State
import yfinance as yf
import datetime as datetime
import pandas as pd

import dash_auth

# Keep this out of source code repository - save in a file or a database
VALID_USERNAME_PASSWORD_PAIRS = {
    'Zahir': 'Nikmal'
}
app = Dash(__name__)
server = app.server

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)


nsdq = pd.read_csv("NASDAQcompanylist.csv")
nsdq.set_index('Symbol', inplace=True)

options = []

for tic in nsdq.index:
    mydict = {'label': f"{nsdq.loc[tic]['Name']} {tic}", 'value': tic}
    options.append(mydict)

app.layout = html.Div([
    html.H1('Stock Ticker Dashboard'),
    html.Div([
        html.H3('Enter Ticker Symbol', style={'paddingRight': '30px'}),
        dcc.Dropdown(id='my-ticker-symbol',
                     options=options,
                     multi=True,
                    )
    ], style={'display': 'inline-block', 'verticalAlign': 'top', 'width': '40%'}),
    html.Div([html.H3('Select a start and end date:'),
              dcc.DatePickerRange(id='my_date_picker',
                                  initial_visible_month=datetime.date.today(),
                                  min_date_allowed=datetime.date(2015, 1, 1),
                                  max_date_allowed=datetime.date.today(),
                                  start_date=datetime.date(2020, 1, 1),
                                  end_date=datetime.date.today(),
                                  with_portal=True)
              ], style={'display': 'inline-block'}),
    html.Div([
        html.Button(id='submit-button',
                    n_clicks=0,
                    children='Submit',
                    style={'fontSize': 24, 'marginLeft': '30px'})
    ]),
    dcc.Graph(id='my_graph',
              figure={'data': [
                  {'x': [1, 2], 'y': [3, 1]}
              ], 'layout': {'title': 'Default Title'}}
              )
])

@app.callback(Output('my_graph', 'figure'),
              [Input('submit-button', 'n_clicks')],
              [State('my-ticker-symbol', 'value'),
               State('my_date_picker', 'start_date'),
               State('my_date_picker', 'end_date')])
def update_graph(n_clicks, stock_ticker, start_date, end_date):
    if not stock_ticker:
        return {'data': [], 'layout': {'title': 'No stock ticker selected'}}

    start = datetime.datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.datetime.strptime(end_date[:10], '%Y-%m-%d')

    traces = []
    for tic in stock_ticker:
        try:
            df = yf.download(tic, start, end)
            traces.append({'x': df.index, 'y': df['Close'], 'name': tic})
        except Exception as e:
            print(f"Error fetching data for {tic}: {e}")

    fig = {'data': traces, 'layout': {'title': ', '.join(stock_ticker)}}
    return fig

if __name__ == '__main__':
    app.run(debug=True, port=8070)
