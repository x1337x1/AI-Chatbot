import os
import asyncio
import logging
import tempfile
from flask import Flask, request
from flask_cors import (CORS, cross_origin)
from multiprocessing import Process
from werkzeug.serving import WSGIRequestHandler
from controllers.open_ai_controller import OpenAiManager
from controllers.pinecone_controller import PineconeManager
from controllers.account_controller import Account
from pydash import get


account = Account()

app = Flask(__name__)
port = int(os.environ.get('SERVER_PORT', 1337))
cors = CORS(app, allow_headers=['Content-Type', 'Access-Control-Allow-Origin',
                                'Access-Control-Allow-Headers', 'Access-Control-Allow-Methods', 'Authorization'])

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')


def parallelize_functions(*functions):
    processes = []
    print("Starting multiple processes")
    for function in functions:
        p = Process(target=function)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


@app.route('/health', methods=['GET'])
@cross_origin()
def get_health_check():
    return print("healthy")

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() 
    email = get(data, 'email') 
    name = get(data, 'name') 
    password = get(data, 'password') 

    if email and name and password:
        register_user = account.signup(data)
        return { "message": register_user }, 200
    else:
        return { "message": register_user }, 400 

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if email and password:
         return account.login(data)
    else:
         return jsonify(error='Email and password are required'), 400




@app.route('/train/website', methods=['POST'])
def train_by_website():
    data = request.get_json() 
    website = get(data, 'website') 
    data_type = get(data, 'data_type') 
    namespace = get(data, 'namespace')  

    if website and data_type and namespace:
        pinecone_manager = PineconeManager()
        embbed_vectors = pinecone_manager.embbed_vectors(website, data_type, namespace)
        return 'AI was trained successfully.', 200
    else:
        return 'Invalid JSON data. Missing required fields.', 400 



@app.route('/query', methods=['POST'])
def query():
    data = request.get_json() 
    query = get(data, 'query') 
    namespace = get(data, 'namespace') 
    chat_history = get(data, 'chat_history')

    if query and namespace:
        open_ai_manager = OpenAiManager()
        answer_query = open_ai_manager.generate_response_chain_with_history(query, namespace, chat_history)
        return str(answer_query), 200
    else:
        return 'Invalid JSON data. Missing required fields.', 400         


def start_server():
    app.run(debug=True)
    app.run(host='0.0.0.0', port=port, threaded=True)
    logging.info('Flask server started successfully.')


if __name__ == '__main__':
    parallelize_functions(start_server)