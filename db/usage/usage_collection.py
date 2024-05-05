from pydash import get
from db.index import MongoDB

USAGE_COLLECTION = 'Usage'


class Usage:
    def __init__(self):
        self.client = MongoDB()

    def insert_usage_document(self, data):
        try:
            tenant_id = get(data, 'tenant_id')
            usage_document = {
                "tenantId": tenant_id,
                "characters_count": 0,
                "queries": 0,
                "test_queries": 0
            }
            tenant_usage_collection = self.client.get_tenant_collection(tenant_id, USAGE_COLLECTION)     
            insert_result = tenant_usage_collection.insert_one(usage_document) 
        except Exception as e:
            print("error while creating new usage docuemnt:", e)   

    def increment_usage(self, data):
        try:
            tenant_id = get(data, 'tenant_id')
            usage_document = {
                "tenantId": tenant_id,
                "characters_count": 0,
                "queries": 0,
                "test_queries": 0
            }
            tenant_usage_collection = self.client.get_tenant_collection(tenant_id, USAGE_COLLECTION)     
            insert_result = tenant_usage_collection.insert_one(usage_document) 
        except Exception as e:
            print("error while creating new usage docuemnt:", e)                