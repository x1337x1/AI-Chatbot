import os
import json
from confluent_kafka import Producer
from dotenv import load_dotenv


load_dotenv()
kafka_url = os.getenv('KAFKA_URL')
TOPIC = "dispatch_panda"

class ProducerController:
    def __init__(self):
        try:
            self.producer = Producer({'bootstrap.servers': kafka_url})
            print("Kafka producer initialized successfully.")
        except Exception as err:
            print(err)

    def delivery_report(self, err, msg):

        if err is not None:
            print('Message delivery failed: {}'.format(err))
        else:
            print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

    def serialize(self, data):
      try:
        return bytes(json.dumps(data), "utf-8")
      except Exception as e:
        print(f"Serialization error: {e}")
        return None  

    def send_answer(self, data, key):
        self.producer.poll(0)
        self.producer.produce(TOPIC, key=key, value=self.serialize(data), callback=self.delivery_report)
        self.producer.flush()

    def send_training_status(self, data, key):
        self.producer.poll(0)
        self.producer.produce(TOPIC, key=key, value=self.serialize(data), callback=self.delivery_report)
        self.producer.flush()