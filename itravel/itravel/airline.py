from database import get_db

class Airline:
    @staticmethod
    def get_all_airlines():
        db = get_db()
        airlines = db.airlines.find()
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