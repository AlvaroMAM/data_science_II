import pandas as pd
import seaborn as sns
import re
import json
from matplotlib import pyplot as plt
from pprint import pprint
from pymongo import MongoClient
from mongoClass import MongoConnectionClass

# Flights fields (Keys) for inserting on MongoDB             
FLIGHTS_FIELDS = ["YEAR", "MONTH", "DAY", "DAY_OF_WEEK", "AIRLINE", "FLIGHT_NUMBER", "TAIL_NUMBER",
             "ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "DEPARTURE_TIME", "DEPARTURE_DELAY", "TAXI_OUT", "WHEELS_OFF", "ELAPSED_TIME", 
             "AIR_TIME", "DISTANCE", "WHEELS_ON", "TAXI_IN" , "ARRIVAL_TIME", "ARRIVAL_DELAY", "DIVERTED", "CANCELLED", 
             "CANCELLATION_REASON", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY", "WEATHER_DELAY"]

NUMBER_OF_FLIGHTS = 500000
FLIGHTS_CSV_NAME='flights_data_frame.csv'
# Getting the flights of a random way 
mongo_client = MongoClient('127.0.0.1', 27017)
mongo_database = mongo_client['data_visualization_project']
flights_collection = mongo_database['flights']
flights_json_testing = flights_collection.aggregate([{"$sample": {"size" : NUMBER_OF_FLIGHTS}}])
print('MESSAGE --> DATA OBTAINED FROM MONGODB')
#df_testing = pd.DataFrame(list(flights_json_testing))
df_testing = pd.read_csv(FLIGHTS_CSV_NAME)
print('MESSAGE --> DATAFRAMES BUILT')

# Una vez tenemos cargado nuestro dataset, vamos a proceder a comprender la información que posee
# Podemos tomar los primeros valores del dataset y estudiarlos, con la función .head() y .tail()que nos devuelven
# los 5 primero valores del dataset y los 5 últimos
print(df_testing.head())
print(df_testing.tail())
# Con esta información podemos observar diferentes variables como pueden ser, Origen del vuelo, destino, atrasos,
# Compañía aérea..., algunas de estas son categoricas pues podemos agrupar los vuelos en función de su origen , 
# destino, compañia.Además con las funcioens .info(), .describe() nos pueden ayudar a conocer más a fondo nuestro dataset.
# Por lo que nos planteamos si existen variables no útiles, o redundantes, duplicadas, existen nomenclaturas con 
# sentido o incluso valores no propios.
print(df_testing.info())
print(df_testing.isna().sum())
print(df_testing.describe())
# Al trabajar el dataset, hay algunos vuelos cuyo valor de aeropuerto no es un acrónimo si no que se encuentra con un número que es el id, debido a la gran
# cantidad de volumen de datos, podemos permitinos desechar estos vuelos.

index_to_delete = []
for index, row in df_testing.iterrows():
    if(bool(re.search(r'\d',row['ORIGIN_AIRPORT']))):
        index_to_delete.append(index)
df_testing = df_testing.drop(index_to_delete)

# Nos centraremos en hacer tomar como dato el arrival_delay poder hacer un dataset más ligero. Para nuestro caso queremos quedarnos 
# con aeropuerto origen, destino, arrival delay, fechas, aerolinea, tiempo de vuelo

df_testing = df_testing.drop("FLIGHT_NUMBER",1)
df_testing = df_testing.drop("TAIL_NUMBER",1)
df_testing = df_testing.drop("DEPARTURE_TIME",1)
df_testing = df_testing.drop("DEPARTURE_DELAY",1)
df_testing = df_testing.drop("TAXI_OUT",1)
df_testing = df_testing.drop("WHEELS_OFF",1)
df_testing = df_testing.drop("ELAPSED_TIME",1)
df_testing = df_testing.drop("DISTANCE",1)
df_testing = df_testing.drop("WHEELS_ON",1)
df_testing = df_testing.drop("TAXI_IN",1)
df_testing = df_testing.drop("ARRIVAL_TIME",1)
df_testing = df_testing.drop("DIVERTED",1)
df_testing = df_testing.drop("CANCELLED",1)
df_testing = df_testing.drop("CANCELLATION_REASON",1)
df_testing = df_testing.drop("SECURITY_DELAY",1)
df_testing = df_testing.drop("LATE_AIRCRAFT_DELAY",1)
df_testing = df_testing.drop("WEATHER_DELAY",1)
df_testing = df_testing.dropna()

# Para poder comenzar a encontrar alguna relación significativa entre variables, podemos calcular la matriz de correlación 
# e imprimir el resultado
corrmat = df_testing.corr()
f, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(corrmat, vmax=.8, square=True);
plt.show()

# Como podemos observar, exite una multicorrelación entre variables, es decir que se pueden realizar preducciones 
# porque existe dependencia lineal entre ellas.
# Por lo tanto, tras estudiar el dataset, consideramos que puede ser interesante, mostrar información acerca de la relación 
# existene entre los vuelos y los atrasos.
# Una vez ya tengamos claro que es posible realizar este tipo de relación, vamos a guardar nuestro dataset 
# para posteriormente generar las graficas

index_to_delete = []
for index, row in df_testing.iterrows():
    if(row['ARRIVAL_DELAY'] <= 0):
        index_to_delete.append(index)
df_testing = df_testing.drop(index_to_delete)

df_testing.to_csv('flights_data_frame.csv')


