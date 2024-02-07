from pymongo import MongoClient

class MongoDBClient:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        self.client = MongoClient(app.config['MONGO_URI'])
        print(self.client)

mongo_client = MongoDBClient()