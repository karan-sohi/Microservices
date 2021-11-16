import connexion
from connexion import NoContent
import json
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from vanilla_cake import VanillaCake
from chocolate_cake import ChocolateCake
import datetime
import logging
import logging.config
import yaml
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

with open ('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')


with open ('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
logger.info(f" Connecting to DB, Hostname: {app_config['datastore']['hostname']}, Port: {app_config['datastore']['port']}")

app_data = app_config['datastore']

DB_ENGINE = create_engine(f"mysql+pymysql://{app_data['user']}:{app_data['password']}@{app_data['hostname']}:{app_data['port']}/{app_data['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)



EVENT_FILE = "events.json"
MAX_EVENTS = 12
EVENT_LIST = []


def get_vanilla_cake_orders(timestamp):
    """Gets new vanilla cake orders after the timestamp"""

    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    readings = session.query(VanillaCake).filter(VanillaCake.date_created >= timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    
    session.close()
    logger.info("Query for Vanilla Cake orders after %s returns %d results"%(timestamp, len(results_list)))
    return results_list, 200


def get_chocolate_cake_orders(timestamp):
    """Gets new chocolate cake orders after the timestamp"""
 
    session = DB_SESSION()
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
    readings = session.query(ChocolateCake).filter(ChocolateCake.date_created >= timestamp_datetime)
    results_list = []
    for reading in readings:
        results_list.append(reading.to_dict())
    
    session.close()
    logger.info("Query for Chocolate Cake orders after %s returns %d results"%(timestamp, len(results_list)))
    return results_list, 200



def order_vanilla_cake(body):
    """Recieves a Vanilla Cake Order"""
    
    session = DB_SESSION()
    vc = VanillaCake(body['cake_id'], 
                     body['name'], 
                     body['vanilla_type'], 
                     body['preparation_method'], 
                     body['sell_by_date']
                     ) 
    session.add(vc)  
    session.commit()
    session.close()
    logger.debug(f"Stored event chocolate cake order request with a unique cake_id of {body['cake_id']} \n")

    return NoContent, 201



def order_chocolate_cake(body):
    """Recieves a Vanilla Cake Order"""
    
    session = DB_SESSION()
    cc = ChocolateCake(body['cake_id'], 
                     body['name'], 
                     body['chocolate_type'], 
                     body['preparation_method'], 
                     body['sell_by_date']
                     )
    session.add(cc)
    session.commit()
    session.close()
    logger.debug(f"Stored event chocolate cake order request with a unique cake_id of {body['cake_id']} \n")
    
    return NoContent, 201


def process_messages():
    """ Process event messages """
    hostname = "%s:%d" % (app_config["events"] ["hostname"], 
                          app_config["events"]["port"])
    retry_count = 0
    while (retry_count < app_config["connect"]["max_retries"]):
        time.sleep(app_config["connect"]["sleep_time"])
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            retry_count = app_config["connect"]["max_retries"]
        except:
            print(f"Trying to connect to Kafka - {retry_count} ")
            retry_count += 1

    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted messages) when the service re-starts (i.e., it doesn't
    # read all the old messages from the history in the message queue). 
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)
    
    # This is blocking - it will wait for a new message

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        payload = msg["payload"]
        logger.debug(payload)

        if msg["type"] == "chocolate":
            # Store the event1 (i.e, the payload) to the DB\
            session = DB_SESSION()
            cc = ChocolateCake(payload['cake_id'], 
                            payload['name'], 
                            payload['chocolate_type'], 
                            payload['preparation_method'], 
                            payload['sell_by_date']
                            )
            session.add(cc)
            session.commit()
            session.close()
            logger.debug(f"Stored event chocolate cake order request with a unique cake_id of {payload['cake_id']} \n")

        elif msg["type"] == "vanilla":
            # Store the event2 (i.e., the payload) to the DB
            session = DB_SESSION()
            vc = VanillaCake(payload['cake_id'], 
                            payload['name'], 
                            payload['vanilla_type'], 
                            payload['preparation_method'], 
                            payload['sell_by_date']
                            ) 
            session.add(vc)  
            session.commit()
            session.close()
            logger.debug(f"Stored event chocolate cake order request with a unique cake_id of {payload['cake_id']} \n")


        # logger.info("Message: %s", %msg)
        
        # print(f"Message = {msg}")
        # print(f"Payload = {payload}")
        # print(f"Message type = {msg['type']}")

        consumer.commit_offsets()



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
