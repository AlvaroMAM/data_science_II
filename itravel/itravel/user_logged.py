from flask_login import UserMixin

class UserLogged(UserMixin):
    def __init__(self, email, name, surname, role, fav_airports, fav_airlines):
        self.email=email
        self.name = name
        self.surname = surname
        self.role = role
        self.fav_airports = fav_airports
        self.fav_airlines = fav_airlines
    def get_id(self):
        return self.email
    def get_name(self):
        return self.name
    def get_surname(self):
        return self.surname
    def get_role(self):
        return self.role
    def get_fav_airports(self):
        return self.fav_airports
    def get_fav_airlines(self):
        return self.fav_airlines