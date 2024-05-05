import sys
sys.dont_write_bytecode = True
import os
import asyncio
from flask import Flask, request
import tempfile
from utils import (returner)
from flask_cors import (CORS, cross_origin)
from multiprocessing import Process
import logging
from werkzeug.serving import WSGIRequestHandler
from controllers.open_ai_controller import OpenAiManager
from controllers.pinecone_controller import PineconeManager
from db.authentication.account_collection import Authentication
from pydash import get
from flask import jsonify
app = Flask(__name__)




cors = CORS(app, allow_headers=['Content-Type', 'Access-Control-Allow-Origin',
                                'Access-Control-Allow-Headers', 'Access-Control-Allow-Methods', 'Authorization'])

ERROR_MSG = "Oops! Something went wrong"
SUCCESS_MSG = "Hooray! Your request was successfully processed"

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
    return returner("healthy")

@app.route('/train/website', methods=['POST'])
def train_by_website():
    json_data = request.get_json() 
    data = get(json_data, 'data') 
    source = get(json_data, 'source') 
    namespace = get(json_data, 'namespace')  
    tenant_id = get(json_data, 'tenant_id')

    if data and source and namespace and tenant_id:
        pinecone_manager = PineconeManager()
        embbed_vectors = pinecone_manager.embbed_vectors(json_data)
        return jsonify({"message": SUCCESS_MSG}), 200
    else:
        return jsonify({"message": ERROR_MSG}), 400

@app.route('/train/inputs', methods=['POST'])
def train_by_inputs():
    json_data = request.get_json() 
    data = get(json_data, 'data') 
    source = get(json_data, 'source') 
    namespace = get(json_data, 'namespace')  
    tenant_id = get(json_data, 'tenant_id')

    if data and source and namespace and tenant_id:
        pinecone_manager = PineconeManager()
        embbed_vectors = pinecone_manager.embbed_vectors(json_data)
        return jsonify({"message": SUCCESS_MSG}), 200
    else:
        return jsonify({"message": ERROR_MSG}), 400

@app.route('/train/delete', methods=['POST'])
def delete_vector_data():
    json_data = request.get_json() 
    vector_ids = get(json_data, 'vector_ids') 
    namespace = get(json_data, 'namespace')  
    tenant_id = get(json_data, 'tenant_id')

    if vector_ids and tenant_id and namespace and tenant_id:
        pinecone_manager = PineconeManager()
        embbed_vectors = pinecone_manager.delete_vector_data(json_data)
        return jsonify({"message": SUCCESS_MSG}), 200
    else:
        return jsonify({"message": ERROR_MSG}), 400

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json() 
    query = get(data, 'question') 
    namespace = get(data, 'namespace') 
    chat_history = get(data, 'chat_history')
    tenant_id = get(data, 'tenant_id')

    if query and namespace and tenant_id:
        open_ai_manager = OpenAiManager()
        answer_query = open_ai_manager.generate_response_chain_with_history(data)
        return jsonify({"message": SUCCESS_MSG}), 200
    else:
        return jsonify({"message": ERROR_MSG}), 400


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json() 
    email = get(data, 'email')
    name = get(data, 'name')
    password = get(data, 'password')

    if email and name and password:
        authentication_class = Authentication()
        response = authentication_class.register(data)
        return jsonify({"message": "Account was registered"}), 200
    else:
        return jsonify({"message": ERROR_MSG}), 400

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() 
    email = get(data, 'email')
    password = get(data, 'password')
    if email and password:
        authentication_class = Authentication()
        response = authentication_class.login(data)
        if response == 200:
            return jsonify({"message": "Login was successful"}), 200
        else:
            return jsonify({"message": "Login Failed"}), 400
    else:
        return jsonify({"message": ERROR_MSG}), 400

def start_server():
    print("Starting server")
    app.run(host='0.0.0.0', port=1337, threaded=True)


if __name__ == '__main__':
    parallelize_functions(start_server)