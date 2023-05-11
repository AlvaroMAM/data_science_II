import json
import pandas as pd
from pymongo import MongoClient
from pprint import pprint


class Queries:
    mongoCollection = None
    
    def __init__(self, db):
        self.db = db
    
    # =================================
    # Gets the airlines with delays and sorts them from the least delay to the most delays
    # =================================
    def get_airlines_with_delays(self):
        mongoCollection = self.db['flights']
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
            json_results.append({
                "airline_name": result['airline_name'],
                "_id": result['_id'],
                "avg_arrival_delay": round(result['avg_arrival_delay'], 2)
            })
        
        return json.dumps(json_results, indent=4)

    # =================================
    # Gets the airlines with no delays
    # =================================
    def get_airlines_with_no_delays(self):
        mongoCollection = self.db['flights']
        pipeline = [
            {"$match": {"CANCELLED": 0, "ARRIVAL_DELAY": 0}},
            {"$group": {"_id": "$AIRLINE"}},
            {"$lookup": {"from": "airlines", "localField": "_id", "foreignField": "IATA_CODE", "as": "airline_info"}},
            {"$project": {"airline_name": {"$arrayElemAt": ["$airline_info.AIRLINE", 0]}, "_id": 1}}
        ]

        results = mongoCollection.aggregate(pipeline)
                
        json_results = []
        for result in results:
            json_results.append({
                "airline_name": result['airline_name'],
                "_id": result['_id']
            })
                
        return json.dumps(json_results, indent=4) 

    # =================================
    # Gets most popular airports and their corresponding cities
    # =================================
    def get_popular_airports(self):
        mongoCollection = self.db['flights']
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
            json_results.append({
                "_id": result['_id'],
                "airport_name": result['airport'],
                "city": result['city'], 
                "flights_count": result['count']
            })
                
        return json.dumps(json_results, indent=4) 
    
    # =================================
    # Gets airlines with cancelled flights
    # =================================
    def get_airlines_with_cancelled_flights(self):
        mongoCollection = self.db['flights']
        pipeline = [
            { "$match": { "CANCELLED": 1 } },
            { "$group": { "_id": "$AIRLINE", "count": { "$sum": 1 } } },
            { "$lookup": { "from": "airlines", "localField": "_id", "foreignField": "IATA_CODE", "as": "airline" } },
            { "$unwind": "$airline" },
            { "$project": { "_id": 1, "airline_name": "$airline.AIRLINE", "airline_iata_code": "$_id", "count": 1 } },
            { "$sort": { "count": -1 } }
        ]


        results = mongoCollection.aggregate(pipeline)
                
        json_results = []
        for result in results:
            json_results.append({
                "iata_code": result['_id'],
                "airline_name": result['airline_name'],
                "cancelled_flights_count": result['count']
            })
                
        return json.dumps(json_results, indent=4) 
    
if __name__ == '__main__':
    try:
        client = MongoClient('localhost', 27017)
        db = client['data_visualization_project']

        queries = Queries(db)

        json = queries.get_airlines_with_cancelled_flights()
        print(json)
        
    except Exception as e:
        print(e)