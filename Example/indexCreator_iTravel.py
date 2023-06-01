#######################################################
# Proyecto: iTravel                                   #
# Autores: Aparicio Morales, Álvaro Manuel            #
#          Kanaan Mohammed Suhail Najm                #
# Asignatura: Ingeniería y Ciencia de Datos II        #
# Máster Universitario en Ingeniería Informática      #
# Universidad de Málaga                               #
#######################################################


from pymongo import MongoClient
import pymongo

# Establecemos conexión con mongoDB
client = MongoClient('localhost', 27017)
db = client['data_science_II_project']

# Creación de Índices en la coleccion flights_processed
db.flights_processed.create_index([('AIRLINE', pymongo.ASCENDING)])
db.flights_processed.create_index([('ORIGIN_AIRPORT', pymongo.ASCENDING)])
db.flights_processed.create_index([('DESTINATION_AIRPORT', pymongo.ASCENDING)])
db.flights_processed.create_index([('DEPARTURE_DELAY', pymongo.ASCENDING)])
db.flights_processed.create_index([('ARRIVAL_DELAY', pymongo.ASCENDING)])
db.flights_processed.create_index([('DEPARTURE_TIME', pymongo.ASCENDING)])
db.flights_processed.create_index([('ARRIVAL_TIME', pymongo.ASCENDING)])
db['flights_processed'].create_index(
    [("CANCELLED", pymongo.ASCENDING)],
    partialFilterExpression={"CANCELLED": 0}
)

