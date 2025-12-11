from pymongo import MongoClient
import certifi

class MongoDBClient:
    def __init__(self):
        self.client = None

    def init_app(self, app):
        self.client = MongoClient(
            app.config['MONGO_URI'],
            tlsCAFile=certifi.where()
        )
        print(self.client)

mongo_client = MongoDBClient()