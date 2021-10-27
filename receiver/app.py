import connexion
from connexion import NoContent
import json
import requests
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient

EVENT_FILE = "events.json"
MAX_EVENTS = 12
EVENT_LIST = []

with open ('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open ('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)
    logger = logging.getLogger('basicLogger')




def order_vanilla_cake(body):
    """Recieves a Vanilla Cake Order"""

    logger.info(f"Received event vanilla cake order request with a unique cake_id of {body['cake_id']} \n")


    client = KafkaClient(hosts=f"{log_config['events']['hostname']}:{log_config['events']['port']}")
    topic = client.topics[str.encode(log_config['events']['topic'])]
    producer = topic.get_sync_producer()

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


    client = KafkaClient(hosts=f"{log_config['events']['hostname']}:{log_config['events']['port']}")
    topic = client.topics[str.encode(log_config['events']['topic'])]
    producer = topic.get_sync_producer()

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
