from database import get_db

class User:
    @staticmethod
    def get_user_by_email(email):
        db = get_db()
        user = db.users.find_one({'EMAIL': email})
        return user
