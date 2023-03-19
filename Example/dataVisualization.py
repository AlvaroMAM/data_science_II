import dash
import dash_html_components as html
import plotly.graph_objects as go
import dash_core_components as dcc
import plotly.express as px
import json
from dash.dependencies import Input, Output
from pymongo import MongoClient
import pandas as pd


FLIGHTS_CSV_NAME='flights_data_frame.csv'

app = dash.Dash()

# Connectamos con la base de datos para leer los aeropuertos y las aerolineas
mongo_client = MongoClient('127.0.0.1', 27017)
mongo_database = mongo_client['data_visualization_project']
airport_collection = mongo_database['airports']
airlines_collection = mongo_database['airlines']
flights_collection = mongo_database['flights']
airport_json = airport_collection.find({})
airlines_json = airlines_collection.find({})

# Tras obtener los datos, crearemos los correspondientes dataframes, por lo que al finalizar este proceso tendremos 3
# airlines.csv, airports.csv, flights.csv
airports_df = pd.DataFrame(list(airport_json))
airlines_df = pd.DataFrame(list(airlines_json))
flights_df = pd.read_csv(FLIGHTS_CSV_NAME)

############################## MAPA ##############################


#Para generar el mapa debemos crearnos un dataset en el que tengamos por cada aeropuerto su media y ordenada
#Para ello el dataset de flights, obtener los vuelos cuyo aeropuerto de origen sea X y calcular la media
airport_delay_mean_json = []
airport_code_processed = set()
for index, row in airports_df.iterrows():
    airport_code = row['IATA_CODE']
    if not (airport_code in airport_code_processed):
        airport_code_processed.add(airport_code)
        flights_airport = flights_df.query('ORIGIN_AIRPORT == @airport_code')
        if (not flights_airport.empty):
            total_delay = flights_airport['ARRIVAL_DELAY'].sum()
            mean_delay = total_delay/float(len(flights_airport.index))
            mean_delay = round(mean_delay,2)
            if(row['LONGITUDE'] and row['LATITUDE'] and row['AIRPORT'] and row['CITY'] and row['STATE']):
                airport_delay_mean_json.append({'AIRPORT_CODE' : airport_code, 'DELAY_MEAN' : mean_delay, 
                'LON': float(row['LONGITUDE'].replace(',','.')), 'LAT': float(row['LATITUDE'].replace(',','.')), 
                'INFO': row['AIRPORT'] + ", "+ row['CITY'] + ", "+row['STATE'] + '<br>MEAN: ' + str(mean_delay) + ' minutes/fly </br>'
                })
airport_delay_mean_df = pd.DataFrame(list(airport_delay_mean_json))
top_5_most_delayed_airport = airport_delay_mean_df.sort_values(by=['DELAY_MEAN', 'AIRPORT_CODE'], ascending=False).head()
top_5_least_delayed_airport = airport_delay_mean_df.sort_values(by=['DELAY_MEAN', 'AIRPORT_CODE'], ascending=False).tail()
maximum_time = top_5_most_delayed_airport['DELAY_MEAN'].max()
minimum_time = top_5_least_delayed_airport['DELAY_MEAN'].max()
if(maximum_time<=0):
    maximum_time=1
if(minimum_time<=0):
    minimum_time=1
#Ahora procederemos a generar el mapa de EEUU con los top 5 aeropuertos 
limits = ["Impuntuales", "Puntuales"]
colors = ["crimson","royalblue"]
fig = go.Figure()
fig.update_layout(
        title_text = 'Top 5 aeropuertos con la mayor y menor media de atrasos en EEUU',
        showlegend = True,
        height = 1000,
        width = 1000,
        geo = dict(
            scope = 'usa',
            landcolor = 'rgb(217, 217, 217)',
        )
    )
lim = limits[0]
fig.add_trace(go.Scattergeo(
    locationmode = 'USA-states',
    lon = top_5_most_delayed_airport['LON'],
    lat = top_5_most_delayed_airport['LAT'],
    text = top_5_most_delayed_airport['INFO'],
    marker = dict(
        size = 25,
        color = colors[0],
        line_color='rgb(40,40,40)',
        line_width=0.5,
        sizemode = 'area'
    ),
    name=limits[0]
))

lim = limits[1]
fig.add_trace(go.Scattergeo(
    locationmode = 'USA-states',
    lon = top_5_least_delayed_airport['LON'],
    lat = top_5_least_delayed_airport['LAT'],
    text = top_5_least_delayed_airport['INFO'],
    marker = dict(
        size = 25,
        color = colors[1],
        line_color='rgb(40,40,40)',
        line_width=0.5,
        sizemode = 'area'
    ),
    name=limits[1]
))

############################## END MAPA ##############################

############################## LINE CHART ##############################

airline_delay_mean_json = []
airline_code_processed = set()
for index, row in airlines_df.iterrows():
    airline_code = row['IATA_CODE']
    if not (airline_code in airline_code_processed):
        airline_code_processed.add(airline_code)
        flights_airline = flights_df.query('AIRLINE == @airline_code')
        if (not flights_airline.empty):
            for year in [2015,2016,2017]:
                flights_airline_year = flights_airline.query('YEAR == @year')
                if (not flights_airline_year.empty):
                    total_delay = flights_airline_year['ARRIVAL_DELAY'].sum()
                    mean_delay = total_delay/float(len(flights_airline_year.index))
                    mean_delay = round(mean_delay,2)
                    airline_delay_mean_json.append({'AIRLINE' : airline_code, 'YEAR' : year ,'DELAY_MEAN' : mean_delay})
airline_delay_mean_df = pd.DataFrame(list(airline_delay_mean_json))
top_5_most_delayed_airlines = airline_delay_mean_df.sort_values(by=['AIRLINE', 'YEAR'], ascending=True)

fig2 = px.line(top_5_most_delayed_airlines, x="YEAR", y="DELAY_MEAN", color='AIRLINE')

############################## LINE CHART ##############################


# Definimos la estructura (layout) de la página web de salida ###################
app.layout = html.Div(children=[
    html.H1(children='ANÁLISIS VISUAL DE DATOS 2022'),

    html.Div(children='''
        Realizado por : Álvaro Manuel Aparicio Morales.
    '''),
    html.Div(children='''
         Graduado en Ingeniería del Software.
    '''),

    dcc.Graph(
        id='bubble-maps',
        figure=fig
    ),
    html.H4('Progresión de medias de aerolíneas'),
    dcc.Graph(
        id='line-chart',
        figure=fig2
    ),
     dcc.Checklist(
        id="checklist",
        options=list(airline_code_processed),
        value=[airline_code_processed.pop(), airline_code_processed.pop()],
        inline=True
    )

])

@app.callback(
    Output("line-chart", "figure"), 
    Input("checklist", "value"))
def update_line_chart(airlines):
    mask = top_5_most_delayed_airlines.AIRLINE.isin(airlines)
    fig = px.line(top_5_most_delayed_airlines[mask], x="YEAR", y="DELAY_MEAN", color='AIRLINE')
    return fig


if __name__ == '__main__': 
    app.run_server()

