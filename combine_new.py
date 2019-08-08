import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime as dt
import flask
import quandl

print(dcc.__version__)

app = dash.Dash()

global df
df = pd.read_csv('zips_2.csv')
df_one = pd.read_csv('zips_one.csv')

df['text'] = 'Zipcode: '+df['ZipCode'].astype(str)+", Rent: "+df['avg_rent'].astype(str)
df_one['text'] = 'Zipcode: '+df_one['ZipCode'].astype(str)+", Rent: "+df_one['avg_rent_one'].astype(str)

app.config.suppress_callback_exceptions = True

#Referenced from: https://dash.plot.ly/urls
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='contents')
])


index_page = html.Div([
	html.H2('House/Apartment Rental Price in the the U.S.'),
    html.Br(),
    dcc.Link('See Rental Prince Trend', href='/trend'),
    html.Br(),
    dcc.Link('Check Average Rental Price for One Bedroom', href='/map_one'),
    html.Br(),
    dcc.Link('Check Average Rental Price for Two Bedroom', href='/map_two'),
])

#Referenced from: https://dash.plot.ly/interactive-graphing
trend_layout = html.Div([
    html.H2('Median House/Apartment Rental Price Trend in the U.S.'),
    html.H6('Data sourced from Zillow using Quandl\'s API'),
    html.H5('Not all states supported. Please check the list below to search.'),
    dcc.Dropdown(
        id='areas',
        options=[{'label': s[0], 'value': str(s[1])}
                 for s in zip(df.City+', '+df.StateCode+', '+df.ZipCode.astype(str), df.ZipCode)],
        value='63130',
        multi=False
    ),
    dcc.Graph(id='trend_graph'),
    html.Br(),
    dcc.Link('Go back to Main Page', href='/'),
    html.Br(),
    dcc.Link('Check Average Rental Price for One Bedroom', href='/map_one'),
    html.Br(),
    dcc.Link('Check Average Rental Price for Two Bedroom', href='/map_two')
])

@app.callback(Output('trend_graph', 'figure'), [Input('areas', 'value')])
def update_graph(value):
    df2b = quandl.get(
        'ZILLOW/Z'+str(value)+'_MRP2B',
        authtoken="TgSaHF_YoDbd65fYqWkU"
        ).reset_index()
    try:
        df1b = quandl.get(
        'ZILLOW/Z'+str(value)+'_MRP1B',
        authtoken="TgSaHF_YoDbd65fYqWkU"
        ).reset_index()
        b1={'type': 'scatter', 'mode': 'lines','x': df1b['Date'],'y': df1b['Value'], 'name': 'One Bedroom'}
        b2={'type': 'scatter', 'mode': 'lines','x': df2b['Date'],'y': df2b['Value'], 'name': 'Two Bedroom'}
        return {'data': [b1] + [b2]}
    except:
        b2={'type': 'scatter', 'mode': 'lines','x': df2b['Date'],'y': df2b['Value'], 'name': 'Two Bedroom'}
        return {'data': [b2]}

#Referenced from: https://dash.plot.ly/getting-started
#Referenced from: https://plot.ly/python/scattermapbox/
map_one_layout = html.Div([
    	html.H3('Average Median Rental Price for One-Bedroom in major cities of the U.S.'),
    	html.Div(id='rent_map_one'),
    	dcc.Graph(id='map_graph_one', figure={
        	'data': [{
            'lat': df_one['Latitude'],
            'lon': df_one['Longitude'],
            'text': df_one['text'],
            'marker': {
                'color': df_one['avg_rent_one'],
                'size': 30,
                'opacity': 0.8
            },
            'customdata': df_one['ZipCode'],
            'type': 'scattermapbox'
        }],
        'layout': {
            'mapbox': {
                'accesstoken': 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw',
            	'center': {
            	'lat': 38.665788,
            	'lon': -90.32224,},
            	'zoom': 3.9
            },
            'hovermode': 'closest',
            'margin': {'l': 15, 'r': 15, 'b': 15, 't': 15}
        	}
    	}),
    html.Br(),
    dcc.Link('Go back to Main Page', href='/'),
    html.Br(),
    dcc.Link('See Rental Prince Trend', href='/trend'),
    html.Br(),
    dcc.Link('Check Average Rental Price for Two Bedroom', href='/map_two')
	])

@app.callback(
    dash.dependencies.Output('rent_map_one', 'children'),
    [dash.dependencies.Input('map_graph_one', 'hoverData')])
def update_text(hoverData):
    s = df_one[df_one['ZipCode'] == hoverData['points'][0]['customdata']]
    return html.H3(
        'Average price in {}, {}, {} is {} over the recent 3 months'.format(
            s.iloc[0]['City'],
            s.iloc[0]['StateCode'],
            s.iloc[0]['ZipCode'],
            s.iloc[0]['avg_rent']
        )
    )

#Referenced from: https://dash.plot.ly/getting-started
map_two_layout = html.Div([
    	html.H3('Average Median Rental Price for Two-Bedroom in major cities of the U.S.'),
    	html.Div(id='rent_map_two'),
    	dcc.Graph(id='map_graph_two', figure={
        	'data': [{
            'lat': df['Latitude'],
            'lon': df['Longitude'],
            'text': df['text'],
            'marker': {
                'color': df['avg_rent'],
                'size': 30,
                'opacity': 0.8
            },
            'customdata': df['ZipCode'],
            'type': 'scattermapbox'
        }],
        'layout': {
            'mapbox': {
                'accesstoken': 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw',
            	'center': {
            	'lat': 38.665788,
            	'lon': -90.32224,},
            	'zoom': 3.9
            },
            'hovermode': 'closest',
            'margin': {'l': 15, 'r': 15, 'b': 15, 't': 15}
        	}
    	}),
    html.Br(),
    dcc.Link('Go back to Main Page', href='/'),
    html.Br(),
    dcc.Link('See Rental Prince Trend', href='/trend'),
    html.Br(),
    dcc.Link('Check Average Rental Price for One Bedroom', href='/map_one')
	])

@app.callback(
    dash.dependencies.Output('rent_map_two', 'children'),
    [dash.dependencies.Input('map_graph_two', 'hoverData')])
def update_text(hoverData):
    s = df[df['ZipCode'] == hoverData['points'][0]['customdata']]
    return html.H3(
        'Average price in {}, {}, {} is {} over the recent 3 months'.format(
            s.iloc[0]['City'],
            s.iloc[0]['StateCode'],
            s.iloc[0]['ZipCode'],
            s.iloc[0]['avg_rent']
        )
    )

#Referenced from: https://dash.plot.ly/urls
@app.callback(dash.dependencies.Output('contents', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/trend':
        return trend_layout
    elif pathname == '/map_one':
        return map_one_layout
    elif pathname == '/map_two':
        return map_two_layout
    else:
        return index_page

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})


if __name__ == '__main__':
    app.run_server(5005)
