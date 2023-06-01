from pymongo import MongoClient
from flask import current_app

def get_db():
    client = MongoClient("mongodb://localhost:27017/itravel")
    db = client["data_science_II_project"]
    return db
