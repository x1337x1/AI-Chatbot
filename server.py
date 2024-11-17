import os
import asyncio
import logging
import tempfile
from pydash import get
from flask import Flask, request
from flask_cors import CORS, cross_origin
from multiprocessing import Process
from werkzeug.serving import WSGIRequestHandler
from controllers.kafka.consumer import KafkaConsumer
from threading import Thread

app = Flask(__name__)
port = int(os.environ.get('SERVER_PORT', 1338))
cors = CORS(app, allow_headers=['Content-Type', 'Access-Control-Allow-Origin',
                                'Access-Control-Allow-Headers', 'Access-Control-Allow-Methods', 'Authorization'])




@app.route('/health', methods=['GET'])
@cross_origin()
def get_health_check():
    return "healthy", 200



def process_queries():
    print("Starting Kafka consumer")
    kafka_consumer_controller = KafkaConsumer()
    asyncio.run(kafka_consumer_controller.start_consumers())


def start_background_tasks():
    thread = Thread(target=process_queries)
    thread.daemon = True  # Daemon threads exit when the main thread exits
    thread.start()


# This will ensure that the background tasks start before the server is fully initialized
start_background_tasks()


if __name__ == '__main__':
    # Parallelize Flask server and Kafka consumer
    app.run(host='0.0.0.0', port=port, threaded=True)
