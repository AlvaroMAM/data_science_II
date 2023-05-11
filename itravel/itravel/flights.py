from database import get_db

class Flight:
    @staticmethod
    def get_flights_by_airline(airline):
        db = get_db()
        flights = db.flights.find({'AIRLINE': airline})
        return flights

    @staticmethod
    def get_most_common_routes():
        db = get_db()
        pipeline = [
            {"$group": {"_id": {"origin": "$ORIGIN_AIRPORT", "destination": "$DESTINATION_AIRPORT"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = db.flights.aggregate(pipeline)
        return list(result)