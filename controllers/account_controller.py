import logging
import os
import bcrypt
import uuid
from dotenv import load_dotenv
from utils.db.index import Database
from controllers.usage_controller import Usage
from pydash import get
from flask import jsonify
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Account:
    def __init__(self):
        self.db = Database()
        self.usage = Usage()


    def signup(self, data):
        try:
            first_name = get(data, 'first_name') 
            last_name = get(data, 'last_name') 
            email = get(data, 'email')  
            password = get(data, 'password')
            tenant_id = str(uuid.uuid4())
            tenant_fingerprint = get(data, 'fingerprint')
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            Account_Collection = self.db.account_collection()
            user_data = {
                'tenant_id': tenant_id,
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'fingerprint': tenant_fingerprint,
                'password': hashed_password.decode('utf-8')  # Decode to store as a string
            }
            Account_Collection.insert_one(user_data) # create account table for tenant
            self.usage.init_usage_collection(tenant_id) # create usage table for tenant

            return jsonify('User Sign Up was successful')

        except Exception as e:
            return jsonify(error='Error retrieving account collection', message=str(e))

    def login(self, data):
        try:
            email = data.get('email')
            password = data.get('password')
    
            # Retrieve user data from MongoDB
            Account_Collection = self.db.account_collection()
            user_data = Account_Collection.find_one({'email': email}) 
            # Check if the password matches
            hashed_password = user_data['password'].encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return jsonify({'message':'Login successful'}), 200
            else:
                return jsonify({'error': 'Invalid username or password'}), 401
    
        except Exception as e:
            return jsonify({'error': str(e)}), 500