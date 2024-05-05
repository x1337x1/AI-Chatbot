import os
from pymongo import MongoClient
from dotenv import load_dotenv
import uuid
from pydash import get
load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_API_KEY'))


    def tenant_database(self, tenant_id):
        try:
            tenant_db = self.client[tenant_id]
            return tenant_db       
        except Exception as e:
            print("error while retreving tenant collection", e)        

    def get_tenant_collection(self, tenant_id, collection):
        try:
            tenant_db = self.client[tenant_id]
            tenant_account_collection = tenant_db[collection]
            return tenant_account_collection            
        except Exception as e:
            print("error while retreving tenant collection", e)         