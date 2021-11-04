import json 
import yaml
import logging
import logging.config
import connexion
from connexion import NoContent
from pykafka import KafkaClient
from flask_cors import CORS,cross_origin


with open ('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')

with open ('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
    logger.info(f" Connecting to DB, Hostname: {app_config['datastore']['hostname']}, Port: {app_config['datastore']['port']}")
    


def get_vanilla_cake_orders(index):
    """ Get Vanilla Cake Order in History"""
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                        app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
                                        consumer_timeout_ms=1000)
                                        
    logger.info("Retrieving vanilla cake order at index %d"% index)
    vanilla_list = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'vanilla':
                vanilla_list.append(msg['payload'])

    except:
        logger.error("No more messages found")


    try: 
        final_value = vanilla_list[index]
        return final_value,201
    except IndexError:
        message = {"message": "Not Found"}
        return message,404



def get_chocolate_cake_orders(index):
    """ Get Chocolate Cake Order in History"""
    hostname = "%s:%d" % (app_config["events"]["hostname"], 
                        app_config["events"]["port"])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True, 
                                        consumer_timeout_ms=1000)
                                        
    logger.info("Retrieving vanilla cake order at index %d"% index)
    chocolate_list = []
    try:
        idx = 0
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'chocolate':
                chocolate_list.append(msg['payload'])

    except:
        logger.error("No more messages found")
     
    try: 
        final_value = chocolate_list[index]
        return final_value,201
    except IndexError:
        message = {"message": "Not Found"}
        return message,404


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS']='Content-Type'
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)
