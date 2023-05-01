import json
import pandas as pd
from pymongo import MongoClient
from pprint import pprint


mongoCollection = None


def get_airlines_with_delays():
    mongoCollection = db['flights']
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

    
if __name__ == '__main__':
    try:
        client = MongoClient('localhost', 27017)
        db = client['data_visualization_project']

        json = get_airlines_with_delays()
        print(json)
    except Exception as e:
        print(e)