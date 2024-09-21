import logging
import os
import bcrypt
import uuid
from dotenv import load_dotenv
from utils.db.index import Database
from pydash import get
from flask import jsonify
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Usage:
    def __init__(self):
        self.db = Database()


    def init_usage_collection(self, tenant_id):
        try:
            
            # Access the collection
            usage_collection = self.db.usage_collection()
            # Create the document structure
            usage_document = {
                'tenant_id': tenant_id,
                'websites_trained': {
                    'allocated': 0,
                    'consumed': 0
                },
                'search_engine_queries': {
                    'allocated': 0,
                    'consumed': 0
                },
                'normal_queries': {
                    'allocated': 0,
                    'consumed': 0
                }
            }
            
            # Insert the document into the collection
            result = usage_collection.insert_one(usage_document)
            print('usage document created')
            return jsonify({'message': 'Document created', 'id': str(result)}), 201
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500