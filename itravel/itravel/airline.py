from database import get_db

class Airline:
    @staticmethod
    def get_all_airlines():
        db = get_db()
        results = db.airlines.find()
        airlines = []
        for result in results:
            airlines.append(AirlineModel(result["_id"], result["IATA_CODE"], result["AIRLINE"]))
        return airlines
    
    @staticmethod
    def get_airline_by_iata(iata_code):
        db = get_db()
        airline = db.airlines.find_one({'IATA_CODE': iata_code})
        return airline
    
    @staticmethod
    def get_airlines_with_most_delays():
        db = get_db()
        pipeline = [
            {"$match": {"$or": [{"DEPARTURE_DELAY": {"$gt": 0}}, {"ARRIVAL_DELAY": {"$gt": 0}}]}},
            {"$group": {"_id": "$AIRLINE", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = db.flights.aggregate(pipeline)
        return list(result)
    
class AirlineModel:
    id = ""
    iata_code = ""
    airline = ""
    
    def __init__(self, id, iata_code, airline):
        self.id = id
        self.iata_code = iata_code
        self.airline = airline