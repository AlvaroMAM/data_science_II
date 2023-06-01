from database import get_db
from flask_login import UserMixin

class User():
    
    def create_user():
        db = get_db()
        user = {
            "NAME": "Alvaro",
            "SURNAME" : "Aparicio",
            "EMAIL" : "alvaro@email.com",
            "PASSWORD" : "test123",
            "ROLE" : "client",
            "FAVOURITES_AIRLINES": [],
            "FAVOURITES_AIRPORTS" : []
        }
        existing_user = db.users.find_one({"EMAIL": user["EMAIL"]})
        if existing_user is None:
            db.users.insert_one(user)
            
    @staticmethod
    def get_user_by_id(id):
        db = get_db()
        user = db.users.find({'_id': id})
        return user

    @staticmethod
    def get_user_by_email(email):
        db = get_db()
        user = db.users.find_one({'EMAIL': email})
        return user
