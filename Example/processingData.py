#######################################################
# Proyecto: iTravel                                   #
# Autores: Aparicio Morales, Álvaro Manuel            #
#          Kanaan Mohammed Suhail Najm                #
# Asignatura: Ingeniería y Ciencia de Datos II        #
# Máster Universitario en Ingeniería Informática      #
# Universidad de Málaga                               #
#######################################################


import json
import pandas as pd
from pymongo import MongoClient
from pprint import pprint

ON_TIME_PERFORMANCE_FIELDS = ["Year", "Month", "DayofMonth", "DayOfWeek", "UniqueCarrier", "FlightNum", "TailNum",
             "Origin", "Dest", "DepTime", "DepDelay", "TaxiOut", "WheelsOff", "ActualElapsedTime", 
             "AirTime", "Distance", "WheelsOn", "TaxiIn" , "ArrTime", "ArrDelay", "Diverted", "Cancelled", 
             "CancellationCode", "SecurityDelay", "LateAircraftDelay", "WeatherDelay"]

# Flights fields (Keys) for inserting on MongoDB             
FLIGHTS_FIELDS = ["YEAR", "MONTH", "DAY", "DAY_OF_WEEK", "AIRLINE", "FLIGHT_NUMBER", "TAIL_NUMBER",
             "ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "DEPARTURE_TIME", "DEPARTURE_DELAY", "TAXI_OUT", "WHEELS_OFF", "ELAPSED_TIME", 
             "AIR_TIME", "DISTANCE", "WHEELS_ON", "TAXI_IN" , "ARRIVAL_TIME", "ARRIVAL_DELAY", "DIVERTED", "CANCELLED", 
             "CANCELLATION_REASON", "SECURITY_DELAY", "LATE_AIRCRAFT_DELAY", "WEATHER_DELAY"]

def insertDataMongoSelectedFields(mongocollection, csvfile, headers_of_csv):
    try:
        flights = pd.read_csv(csvfile, delimiter=',',low_memory=False)
        print("CSV readed --> ", csvfile)
        flights_json = json.loads(flights.to_json(orient='records'))
        correct_flights_json_list = [] # Flights that have corrected fields, without empty or None
        for flight in flights_json:
            correct_flight_json = {} # Json that contains the pair KV of attributes for insert on MongoDB
            field_position = 0
            for field in headers_of_csv:
                correct_flight_json.update({FLIGHTS_FIELDS[field_position] : flight[field]})
                field_position = field_position + 1
            correct_flights_json_list.append(correct_flight_json)
        if correct_flights_json_list:
            mongocollection.insert_many(correct_flights_json_list)
            print("|-----------------------------------O-----------------------------------|")
            print("Message --> ",csvfile," inserted successfully")
            print("|-----------------------------------O-----------------------------------|")
        else:
            print("|-----------------------------------O-----------------------------------|")
            print("Message --> ",csvfile," No flights inserted")
            print("|-----------------------------------O-----------------------------------|")
    except Exception as e:
        print("|-----------------------------------O-----------------------------------|")
        print("Exception during processing of ",csvfile," --> ",e)
        print("|-----------------------------------O-----------------------------------|")
        return False

def insertDataMongo(mongocollection, csvfile):
    try:
        data = pd.read_csv(csvfile, delimiter=';')
        mongocollection.insert_many(json.loads(data.to_json(orient='records')))
        print("|-----------------------------------O-----------------------------------|")
        print("Message --> ",csvfile," inserted successfully")
        print("|-----------------------------------O-----------------------------------|")
        return True
    except Exception as e:
        print("|-----------------------------------O-----------------------------------|")
        print("Exception during processing of ",csvfile," --> ",e)
        print("|-----------------------------------O-----------------------------------|")
        return False

# Create connection to local db
try:
    client = MongoClient('localhost', 27017)
    db = client['data_science_II_project']
    print("|-----------------------------------O-----------------------------------|")
    print("Message --> Connection with database established")
    print("|-----------------------------------O-----------------------------------|")
    mongoCollection = db['airports']
    insertDataMongo(mongoCollection,'dataset/airports.csv')
    mongoCollection = db['airlines']
    insertDataMongo(mongoCollection,'dataset/airlines.csv')
    mongoCollection = db['flights']
    insertDataMongoSelectedFields(mongocollection=mongoCollection, csvfile='dataset/flights.csv', headers_of_csv=FLIGHTS_FIELDS)
    print("|-----------------------------------O-----------------------------------|")
    print("Message --> dataset/flights.csv has been successfully processed")
    print("|-----------------------------------O-----------------------------------|")
    for year in ["6","7"]:
        for month in ["1","2","3","4","5","6", "7", "8", "9", "10", "11", "12"]:
            file_name = "dataset/On_Time_On_Time_Performance_201" + year + "_" + month + ".csv"
            insertDataMongoSelectedFields(mongocollection=mongoCollection, csvfile=file_name, headers_of_csv=ON_TIME_PERFORMANCE_FIELDS)
            print("|-----------------------------------O-----------------------------------|")
            print("Message --> ", file_name, "has been successfully processed")
            print("|-----------------------------------O-----------------------------------|")
    
except Exception as e:
    print(e)
