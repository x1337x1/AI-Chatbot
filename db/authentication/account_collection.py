import uuid
from pydash import get
from db.index import MongoDB
from db.usage.usage_collection import Usage
import bcrypt

ACCOUNT_COLLECTION = 'Account'

class Authentication:
    def __init__(self):
        self.client = MongoDB()
        self.usage_collection = Usage()

    def register(self, data):
        try:
            print("registering a new user")
            email = get(data, 'email')
            name = get(data, 'name')
            password = get(data, 'password')
            tenant_id = self.generate_tenant_id(email, password)
            tenant_db = self.client.tenant_database(tenant_id)
            tenant_account_collection = self.client.get_tenant_collection(tenant_id, ACCOUNT_COLLECTION)
            if tenant_account_collection.find_one({"email": email}):
                return str("Email already exists. Please use a different email.")
            else:
                hashed_password = self.hash_password(password)
                account_document = {
                    "tenant_id": tenant_id,
                    "email": email,
                    "name": name,
                    "password": hashed_password
                }
                insert_account_result = tenant_account_collection.insert_one(account_document)
                insert_usage_result = self.usage_collection.insert_usage_document(account_document)
                return str("Account was registered")
        except Exception as e:
            print("error while creating an account:", e)


    def login(self, data):
        try:
            print("user is logging to his account")
            email = get(data, 'email')
            password = get(data, 'password')
            tenant_id = self.generate_tenant_id(email, password)   
            tenant_account_collection = self.client.get_tenant_collection(tenant_id, ACCOUNT_COLLECTION)
            account_document = tenant_account_collection.find_one({"email": email})
            if account_document:
                hashed_password = account_document.get('password')
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    return 200
            else:
                return 400
        except Exception as e:
            print("error while login:", e)
                    

    def generate_tenant_id(self, email, password):
        try:
            user_data = email + password
            hashed_data = uuid.uuid5(uuid.NAMESPACE_DNS, user_data)
            generated_id = str(hashed_data)
            return generated_id
        except Exception as e:
            print("error while generating tenant id", e)

    def hash_password(self, password):
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            return hashed_password.decode('utf-8')
        except Exception as e:
            print("error while hashing password:", e)    



