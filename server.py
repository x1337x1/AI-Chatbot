import asyncio
from flask import (Flask)
from utils import (returner)
from flask_cors import (CORS, cross_origin)
from multiprocessing import Process
import logging
from werkzeug.serving import WSGIRequestHandler

# Redirect Werkzeug logs to a null handler to suppress them
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)
app = Flask(__name__)

# Configure your own logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



cors = CORS(app, allow_headers=['Content-Type', 'Access-Control-Allow-Origin',
                                'Access-Control-Allow-Headers', 'Access-Control-Allow-Methods', 'Authorization'])

def parallelize_functions(*functions):
    processes = []
    logger.info("Starting multiple processes")
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


def start_server():
    logger.info("Starting server")
    app.run(host='0.0.0.0', port=1337, debug=True, threaded=True)


if __name__ == '__main__':
    parallelize_functions(start_server)