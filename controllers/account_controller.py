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


class Account:
    def __init__(self):
        self.db = Database()


    def signup(self, data):
        try:
            name = get(data, 'name') 
            email = get(data, 'email')  
            password = get(data, 'password')
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            Account_Collection = self.db.account_collection()
            user_data = {
                'user_id': str(uuid.uuid4()),
                'name': name,
                'email': email,
                 'password': hashed_password.decode('utf-8')  # Decode to store as a string
            }
            document = Account_Collection.insert_one(user_data)
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