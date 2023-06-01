#######################################################
# Proyecto: iTravel                                   #
# Autores: Aparicio Morales, Álvaro Manuel            #
#          Kanaan Mohammed Suhail Najm                #
# Asignatura: Ingeniería y Ciencia de Datos II        #
# Máster Universitario en Ingeniería Informática      #
# Universidad de Málaga                               #
#######################################################
from pymongo import MongoClient
import pandas as pd
import re
import numpy as np

# Configura la conexión a MongoDB
client = MongoClient('localhost', 27017)
db = client['data_science_II_project']
cursor = db['flights'].find()

batch_size = 5000  # define el tamaño del lote
batch = []  # inicializa la lista para el lote


for idx, doc in enumerate(cursor):
    # procesa cada documento aquí
    # por ejemplo, crea un nuevo campo 'FLIGHT_DATE'
    doc['FLIGHT_DATE'] = pd.to_datetime(doc['YEAR']*10000 + doc['MONTH']*100 + doc['DAY'],format='%Y%m%d')
    batch.append(doc)

    if (idx + 1) % batch_size == 0:
        # procesa el lote cuando alcance el tamaño del lote
        df = pd.DataFrame(batch)
        df = df.dropna()
        df['IS_DELAYED'] = (df['DEPARTURE_DELAY'] > 0).astype(int)
        # Al trabajar el dataset, hay algunos vuelos cuyo valor de aeropuerto no es un acrónimo si no que se encuentra con un número que es el id, debido a la gran
        # cantidad de volumen de datos, podemos permitinos desechar estos vuelos.
        index_to_delete = []
        for index, row in df.iterrows():
            if(bool(re.search(r'\d',row['ORIGIN_AIRPORT']))):
                index_to_delete.append(index)
        df = df.drop(index_to_delete)
        # Inserta el DataFrame en la nueva colección
        df_to_dict = df.to_dict('records')
        if bool(df_to_dict):
            db['flights_processed'].insert_many(df_to_dict)
        
        # resetea el lote
        batch = []

# No olvides el último lote si su tamaño es menor que el tamaño del lote
if batch:
    df = pd.DataFrame(batch)
    db['flights_processed'].insert_many(df.to_dict('records'))
