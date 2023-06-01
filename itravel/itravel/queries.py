import json
import pandas as pd
from pymongo import MongoClient
from pprint import pprint
from database import get_db

class Queries:
    mongoCollection = None
    db = get_db()
    airlines_with_cancelled_flights = []
    airlines_security_delays = []
    airlines_delays = []
    airlines_no_delays = []
    airlines_with_most_travelled_distance = []
    popular_airports = []
    airports_with_most_traffic = []
    
    fav_airlines_iata = []
    fav_airports_iata = []
    
    # =================================
    # Gets the airlines with delays and sorts them from the least delay to the most delays
    # =================================
    def get_airlines_with_delays(self):
        mongoCollection = self.db.flights
        pipeline = [
        { "$match": { "CANCELLED": 0, "ARRIVAL_DELAY": { "$lte": 0 } } },
        { "$group": { "_id": "$AIRLINE", "avg_arrival_delay": { "$avg": "$ARRIVAL_DELAY" } } },
        { "$lookup": { "from": "airlines", "localField": "_id", "foreignField": "IATA_CODE", "as": "airline_info" } },
        { "$project": { "airline_name": { "$arrayElemAt": [ "$airline_info.AIRLINE", 0 ] }, "avg_arrival_delay": 1 } },
        { "$sort": { "avg_arrival_delay": -1 } }
        ]   

        results = mongoCollection.aggregate(pipeline)
        
        json_results = []
        for result in results:
            if result['_id'] in self.fav_airlines_iata:
                json_results.append({
                        "airline_name": result['airline_name'],
                        "_id": result['_id'],
                        "avg_arrival_delay": round(result['avg_arrival_delay'], 2)
                })
        
        return json_results

    # =================================
    # Gets the airlines with no delays
    # =================================
    def get_airlines_with_no_delays(self):
        mongoCollection = self.db
        pipeline = [
            {"$match": {"CANCELLED": 0, "ARRIVAL_DELAY": 0}},
            {"$group": {"_id": "$AIRLINE"}},
            {"$lookup": {"from": "airlines", "localField": "_id", "foreignField": "IATA_CODE", "as": "airline_info"}},
            {"$project": {"airline_name": {"$arrayElemAt": ["$airline_info.AIRLINE", 0]}, "_id": 1}}
        ]
        
        db = get_db()
        users_collection = db.users
        fav_airliens = users_collection.find()[0]['FAVOURITES_AIRLINES']
        
        flights = db['flights_processed'].find({
            "$or": [
                {"CANCELLED": 1},  # Vuelos cancelados
                {"ARRIVAL_DELAY": {"$gt": 0}}  # Vuelos con retraso
            ]
        }, {"AIRLINE": 1})
        
        unique_airlines = set()
        for flight in flights:
            unique_airlines.add(flight["AIRLINE"])
            
        results = []
        for airline in fav_airliens:
            if airline["iata_code"] in unique_airlines:
                results.add(airline)
        
        json_results = []
        for result in results:
            if result['_id'] in self.fav_airlines_iata:
                json_results.append({
                    "airline_name": result['airline_name'],
                    "_id": result['_id']
                })
                
        return json_results

    # =================================
    # Gets most popular airports and their corresponding cities
    # =================================
    def get_popular_airports(self):
        mongoCollection = self.db.flights
        pipeline = [
            {"$match": {"CANCELLED": 0}},
            {"$group": {"_id": "$DESTINATION_AIRPORT", "count": {"$sum": 1}}},
            {"$lookup": {"from": "airports", "localField": "_id", "foreignField": "IATA_CODE", "as": "airport_info"}},
            {"$unwind": "$airport_info"},
            {"$project": {"_id": 1, "airport": "$airport_info.AIRPORT", "city": "$airport_info.CITY", "count": 1}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]

        results = mongoCollection.aggregate(pipeline)
                
        json_results = []

        for result in results:
            if result['_id'] in self.fav_airports_iata:
                json_results.append({
                    "_id": result['_id'],
                    "airport_name": result['airport'],
                    "city": result['city'], 
                    "flights_count": result['count']
                })
                
        return json_results
    
    # =================================
    # Gets airlines with cancelled flights
    # =================================
    def get_airlines_with_cancelled_flights(self):

        pipeline = [
            { "$match": { "CANCELLED": 1 } },
            { "$group": { "_id": "$AIRLINE", "count": { "$sum": 1 } } },
            { "$lookup": { "from": "airlines", "localField": "_id", "foreignField": "IATA_CODE", "as": "airline" } },
            { "$unwind": "$airline" },
            { "$project": { "_id": 1, "airline_name": "$airline.AIRLINE", "airline_iata_code": "$_id", "count": 1 } },
            { "$sort": { "count": 1 } }
        ]


        results = self.db.flights.aggregate(pipeline)
                
        json_results = []
        for result in results:
            if result['_id'] in self.fav_airlines_iata:
                json_results.append({
                    "iata_code": result['_id'],
                    "airline_name": result['airline_name'],
                    "cancelled_flights_count": result['count']
                })
                
        return json_results

    # =================================
    # get_airports_with_most_traffic
    # =================================
    def get_airports_with_most_traffic(self):
        mongoCollection = self.db.flights
        pipeline_dst = [
            {"$match": {"CANCELLED": 0}},
            {"$group": {"_id": "$DESTINATION_AIRPORT", "count": {"$sum": 1}}},
            {"$lookup": {"from": "airports", "localField": "_id", "foreignField": "IATA_CODE", "as": "airport_info"}},
            {"$unwind": "$airport_info"},
            {"$project": {"_id": 1, "airport": "$airport_info.AIRPORT", "city": "$airport_info.CITY", "count": 1}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        pipeline_origin = [
            {"$match": {"CANCELLED": 0}},
            {"$group": {"_id": "$ORIGIN_AIRPORT", "count": {"$sum": 1}}},
            {"$lookup": {"from": "airports", "localField": "_id", "foreignField": "IATA_CODE", "as": "airport_info"}},
            {"$unwind": "$airport_info"},
            {"$project": {"_id": 1, "airport": "$airport_info.AIRPORT", "city": "$airport_info.CITY", "count": 1}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]

        destinations = list(self.db.flights.aggregate(pipeline_dst))
        origins = list(self.db.flights.aggregate(pipeline_origin))
        
        results = []
        for dest in destinations:
            for orig in origins:
                if dest['_id'] == orig['_id']:
                    results.append({
                        '_id': dest['_id'],
                        'airport': dest['airport'],
                        'city': dest['city'],
                        'total_count': dest['count'] + orig['count'],
                        'destination_count': dest['count'],
                        'origin_count': orig['count']
                    })
                    origins.remove(orig)
                    break
            else:
                results.append({
                    '_id': dest['_id'],
                    'airport': dest['airport'],
                    'city': dest['city'],
                    'total_count': dest['count'],
                    'destination_count': dest['count'],
                    'origin_count': 0
                })

        for orig in origins:
            results.append({
                '_id': orig['_id'],
                'airport': orig['airport'],
                'city': orig['city'],
                'total_count': orig['count'],
                'destination_count': 0,
                'origin_count': orig['count']
            })

        results.sort(key=lambda x: x['total_count'], reverse=True)
                      
        json_results = []
        for result in results:
            if result['_id'] in self.fav_airports_iata:
                json_results.append({
                    "_id": result['_id'],
                    "airport_name": result['airport'],
                    "city": result['city'], 
                    "total_flights_count": result['total_count'],
                    "destination_count": result['destination_count'],
                    "origin_count": result['origin_count'],
                })
            
        return json_results

    # =================================
    # Gets the airlines with most travelled distance
    # =================================
    def get_airlines_with_most_travelled_distance(self):
        mongoCollection = self.db.flights
        pipeline = [
            { "$match": {"CANCELLED": 0, "DISTANCE": {"$exists": True}} },
            { "$group": { "_id": "$AIRLINE", "total_distance": {"$sum": "$DISTANCE"}}},
            { "$lookup": { "from": "airlines", "localField": "_id", "foreignField": "IATA_CODE", "as": "airline_info" } },
            { "$unwind": "$airline_info" },
            { "$project": {  "_id": 1, "airline": "$airline_info.AIRLINE", "total_distance": 1 }},
            { "$sort": {"total_distance": 1} },
        ]

        results = mongoCollection.aggregate(pipeline)
                
        json_results = []
        for result in results:
            if result['_id'] in self.fav_airlines_iata:
                json_results.append({
                    "_id": result['_id'],
                    "airline_name": result['airline'],
                    "total_distance": result['total_distance']
                })
                
        return json_results
    
    
    # =================================
    # Gets the airlines with most flights that has security delays
    # =================================
    def get_airlines_with_security_delays(self):
        mongoCollection = self.db.flights
        pipeline = [
            { "$match": { "SECURITY_DELAY": {"$gt": 0} } },
            { "$group": { "_id": "$AIRLINE", "count": {"$sum": 1} } },
            { "$lookup": { "from": "airlines", "localField": "_id", "foreignField": "IATA_CODE", "as": "airline_info" } },
            { "$unwind": "$airline_info" },
            { "$project": { "_id": 1, "airline": "$airline_info.AIRLINE", "count": 1 } },
            { "$sort": {"count": 1} },
        ]

        results = mongoCollection.aggregate(pipeline)
                
        json_results = []
        for result in results:
            if result['_id'] in self.fav_airlines_iata:
                json_results.append({
                    "_id": result['_id'],
                    "airline_name": result['airline'],
                    "total_flights_security_delay": result['count']
                })
                
        return json_results
    
    def perform_airlines_queries(self, airlines):
        self.fav_airlines_iata = []
        for item in airlines:
            self.fav_airlines_iata.append(str(item["iata_code"]))
            
        self.airlines_delays = self.get_airlines_with_delays()
        self.airlines_no_delays = self.get_airlines_with_no_delays()
        self.airlines_with_cancelled_flights = self.get_airlines_with_cancelled_flights()
        self.airlines_security_delays = self.get_airlines_with_security_delays()
        self.airlines_with_most_travelled_distance = self.get_airlines_with_most_travelled_distance()
        
        
    def perform_airports_queries(self, airports):
        self.fav_airports_iata = []

        for item in airports:
            self.fav_airports_iata.append(str(item["iata_code"]))
        
        self.popular_airports = self.get_popular_airports()
        self.airports_with_most_traffic = self.get_airports_with_most_traffic()
        print(self.airports_with_most_traffic)
        
    def filter_airlines_queries(self, ids):
        filtered1 = []
        filtered2 = []
        filtered3 = []
        filtered4 = []
        filtered5 = []
        
        for airline in self.airlines_delays:
            print(airline)
            if airline["_id"] in ids:
                filtered1.append(airline)
                
        for airline in self.airlines_security_delays:
            if airline["_id"] in ids:
                filtered2.append(airline)
                
        for airline in self.airlines_with_cancelled_flights:
            if airline["iata_code"] in ids:
                filtered3.append(airline)
                
        for airline in self.airlines_with_most_travelled_distance:
            if airline["_id"] in ids:
                filtered4.append(airline)
                
        for airline in self.airlines_no_delays:
            if airline["_id"] in ids:
                filtered5.append(airline)
                
        return filtered1, filtered2, filtered3, filtered4, filtered5

    def filter_airports_queries(self, ids):
        filtered1 = []
        filtered2 = []

        for airport in self.popular_airports:
            if airport["_id"] in ids:
                filtered1.append(airport)
                
        for airport in self.airports_with_most_traffic:
            if airport["_id"] in ids:
                filtered2.append(airport)
                
                
        return filtered1, filtered2