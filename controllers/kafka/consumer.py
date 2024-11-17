import os
from confluent_kafka import Consumer
from controllers.pinecone_controller import PineconeManager
from controllers.open_ai_controller import QueryHandler
import asyncio
import json
from dotenv import load_dotenv
load_dotenv()
kafka_url = os.getenv('KAFKA_URL', 'localhost')

topics = ['process_koala']
training_event_input = 'koala_training_input'
training_event_file = 'koala_training_file'
training_event_url = 'koala_training_url'
query_event = 'koala_query'


class KafkaConsumer:
    def __init__(self):
        self.consumer = self.initialize_kafka_consumers()
        self.training_handler = PineconeManager()
        self.query_handler = QueryHandler()
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
                        self.training_handler.train_by_input(data)
                    elif(event == training_event_url):
                        self.training_handler.train_by_url(data) 
                    elif(event == training_event_file):
                        ## call function to process file
                        print('train by file')   
                    elif(event == query_event):
                        self.query_handler.generate_response_chain_with_history(data)         
                else:
                    print("Unrecognised topic:", topic)
            except Exception as err:
                print(err)
     

    async def start_consumers(self):
        # Start processing messages with both consumers in parallel
            await asyncio.gather(self.process_events(self.consumer))
            