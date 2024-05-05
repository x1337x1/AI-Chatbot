from pydash import get
from db.index import MongoDB

RECORD_COLLECTION = 'Record'


class Record:
    def __init__(self):
        self.client = MongoDB()

    def insert_record_document(self, data):
        try:
            tenant_id = get(data, 'tenant_id')
            source = get(data, 'source')
            vector_ids = get(data, 'vector_ids')
            characters_count = get(data, 'characters_count')
            record_document = {
                "tenant_id": tenant_id,
                "source": source,
                "vector_ids": vector_ids,
                "characters_count": characters_count,
            }
            tenant_record_collection = self.client.get_tenant_collection(tenant_id, RECORD_COLLECTION)     
            insert_result = tenant_record_collection.insert_one(record_document) 
        except Exception as e:
            print("error while creating new record docuemnt:", e)   
               