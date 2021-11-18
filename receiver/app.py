import connexion
from connexion import NoContent
import json
import requests
import yaml
import logging
import logging.config
import datetime
import json
import time
from pykafka import KafkaClient
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_conf = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

EVENT_FILE = "events.json"
MAX_EVENTS = 12
EVENT_LIST = []

with open ('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open ('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')
    
retry_count = 0
while (retry_count < app_config["connect"]["max_retries"]):
        time.sleep(app_config["connect"]["sleep_time"])
        try:
            client = KafkaClient(hosts=f"{log_config['events']['hostname']}:{log_config['events']['port']}")
            topic = client.topics[str.encode(log_config['events']['topic'])]
            producer = topic.get_sync_producer()
            logger.info(f"The connection has been established {retry_count}")
            retry_count = app_config["connect"]["max_retries"]
        except:
            logger.info(f"Connection not established. Still loading. {retry_count}")
        retry_count += 1


def order_vanilla_cake(body):
    """Recieves a Vanilla Cake Order"""

    logger.info(f"Received event vanilla cake order request with a unique cake_id of {body['cake_id']} \n")
   

    msg = { "type": "vanilla", 
            "datetime":
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
                    "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config['eventstore1']['url'],
    #                         json=body, headers=headers)

    logger.info(f"Returned event vanilla cake order response (Id:{body['cake_id']} with status code 201 \n")

    return NoContent, 201



def order_chocolate_cake(body):
    """ Receives a chocolate cake order event """

    logger.info(f"Received event chocolate cake order request with a unique cake_id of {body['cake_id']} \n")
   

    msg = { "type": "chocolate", 
            "datetime":
                datetime.datetime.now().strftime(
                    "%Y-%m-%dT%H:%M:%S"),
                    "payload": body }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    # headers = {"content-type": "application/json"}
    # response = requests.post(app_config['eventstore2']['url'],
    #                         json=body, headers=headers)

    logger.info(f"Returned event chocolate cake order response (Id:{body['cake_id']} with status code 201 \n")

    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
