import logging
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()
MONGO_DB_URL = os.getenv('MONGO_DB_URL')

class Database:
    def __init__(self):
        self.client = MongoClient(MONGO_DB_URL)
        self.db = self.client['UDB']

    def init_connection(self):
        try:
            self.client = MongoClient(MONGO_DB_URL)
            self.db = self.client['UDB']
            logging.info(f'Successfully connected to MongoDB database')
        except Exception as e:
            print('Error connecting to MongoDB:', e)

    def account_collection(self):
        try:
            collection = self.db['Accounts']
            print('Account collection retrieved')
            return collection

        except Exception as e:
            print('Error retrieving account collection:', e)
            return None

    def usage_collection(self):
        try:
            collection = self.db['Usage']
            print('Usage collection retrieved')
            return collection

        except Exception as e:
            print('Error retrieving usage collection:', e)
            return None