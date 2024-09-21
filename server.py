import os
import asyncio
import logging
import tempfile
from pydash import get
from flask import Flask, request
from flask_cors import (CORS, cross_origin)
from multiprocessing import Process
from werkzeug.serving import WSGIRequestHandler
from routes.authentication import auth_routes
from routes.queries import queries_routes, search_engine_routes
from routes.training import training_routes



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



def start_server():
    app.run(debug=True)
    app.run(host='0.0.0.0', port=port, threaded=True)
    logging.info('Flask server started successfully.')


if __name__ == '__main__':
    auth_routes(app)
    queries_routes(app)
    search_engine_routes(app)
    training_routes(app)
    parallelize_functions(start_server)