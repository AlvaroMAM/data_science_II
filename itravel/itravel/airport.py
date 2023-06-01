from database import get_db

class Airport:
    @staticmethod
    def get_all_airports():
        db = get_db()
        resutls = db.airports.find()
        airports = []
        for result in resutls:
            airports.append(AirportModel(result["_id"],
                                         result["IATA_CODE"],
                                         result["AIRPORT"],
                                         result["CITY"],
                                         result["STATE"], 
                                         result["COUNTRY"]))

        return airports
    
    @staticmethod
    def get_airport_by_iata(iata_code):
        db = get_db()
        airport = db.airports.find_one({'IATA_CODE': iata_code})
        return airport

    @staticmethod
    def get_airports_with_most_cancellations():
        db = get_db()
        pipeline = [
            {"$match": {"CANCELLED": 1}},
            {"$group": {"_id": "$ORIGIN_AIRPORT", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        result = db.flights.aggregate(pipeline)
        return list(result)

class AirportModel:
    id = ""
    iata_code = ""
    airport = ""
    city = ""
    state = ""
    country = ""
    
    def __init__(self, id, iata_code, airport, city, state, country):
        self.id = id
        self.iata_code = iata_code
        self.airport = airport
        self.city = city
        self.state = state
        self.country = country