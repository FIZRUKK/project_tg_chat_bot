from app.database.requests.managers import *


class DatabaseManager:
    def __init__(self):
        self.users = UserManager()

db_manager = DatabaseManager()