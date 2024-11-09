import os
from confluent_kafka import Consumer
from controllers.pinecone_controller import PineconeManager
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
kafka_url = os.getenv('KAFKA_URL', 'localhost')

topics = ['process_koala']
training_event_input = 'nervana_training_input'
training_event_file = 'nervana_training_file'
training_event_url = 'nervana_training_url'

class KafkaConsumer:
    def __init__(self):
        self.consumer = self.initialize_kafka_consumers()
        self.training_handler = PineconeManager()
        self.running = True  

    def initialize_kafka_consumers(self):
        try:
            consumer = Consumer({
                'bootstrap.servers': kafka_url,
                'group.id': 'broker',
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': True,
            })
            consumer.subscribe(topics)
            print("Kafka consumer initialized successfully For Topics:", topics)
            return consumer

        except Exception as err:
            print(err)


    def shutdown(self, signum, frame):
        self.running = False
        self.consumer.close()
    

    async def process_events(self, consumer):
        while self.running:
            try:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    print(msg.error())
                    continue
                topic = msg.topic()    
                event = json.loads(msg.value()).get('event')
                data = json.loads(msg.value()).get('data')
                
                print("Event ", event)
                print('Data', data)
                if(topic == topics[0]):
                    if(event == training_event_input):  
                        print('process input data', data)   
                        self.training_handler.train_by_input(data)
                    elif(event == training_event_url):
                        self.training_handler.train_by_website(data) 
                    elif(event == training_event_file):
                        ## call function to process file
                        print('train by file')                                 
                else:
                    print("Unrecognised topic:", topic)
            except Exception as err:
                print(err)
     

    async def start_consumers(self):
        # Start processing messages with both consumers in parallel
            await asyncio.gather(self.process_events(self.consumer))
            