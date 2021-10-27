import connexion
from connexion import NoContent
import json
import requests
import os
import datetime
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler

EVENT_FILE = "events.json"
MAX_EVENTS = 12
EVENT_LIST = []

with open ('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

with open ('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config) 
    logger = logging.getLogger('basicLogger')

def populate_stats():
    """Periodically update stats"""
    logger.info("Periodic Processing Started")
    current_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S.%f")


    # Check if data.json file exists, If it doesen't, then this block will create the new file with starting values
    check_data_file = os.path.isfile("./data.json")
    if check_data_file == False:
        starting_data = {
        "num_vanilla_orders": 0,
        "num_chocolate_orders": 0,
        "max_vanilla_orders": "No Vanilla Cakes Ordered",
        "max_chocolate_orders": "No Chocolate Cakes Ordered",
        "last_updated": current_time
        }
        with open(app_config["datastore"]["filename"], "w") as json_file:
            json_file.write(json.dumps(starting_data))


    # This will read the last updated value from data.json file and update the parameters for GET endpoint to Storage
    with open(app_config["datastore"]["filename"], "r") as json_file:
        content = json.loads(json_file.read())
        params = {
            "timestamp": content["last_updated"] + 'Z'
        }


    # GET the data from the Storage Service
    vanilla_response = requests.get(f"{app_config['eventstore']['url']}/inventory/vanillacake", params=params)
    chocolate_response = requests.get(f"{app_config['eventstore']['url']}/inventory/chocolatecake", params=params)

    print(f"Vanilla Response: {vanilla_response}")
    print(f"Chocolate Content: {chocolate_response}")

    # Check if the response is correct from Storage, then calculate the total number of orders received from both the endpoints
    if (vanilla_response.status_code == 200) and (chocolate_response.status_code == 200):
        vanilla_content = json.loads(vanilla_response.text)
        chocolate_content = json.loads(chocolate_response.text)
        total_events = len(vanilla_content) + len(chocolate_content)
        logger.info(f"{total_events} events received")
    else:
        logger.error("Error in GET endpoint of Data Storage Service.")


    # Vanilla Calculations

    # Adds the events received from Storage and events that were in data.json file in variable
    with open(app_config["datastore"]["filename"], "r") as json_file:
        content = json.loads(json_file.read())
        num_vanilla_orders = len(vanilla_content) + content["num_vanilla_orders"]
        num_chocolate_orders = len(chocolate_content) + content["num_chocolate_orders"]


    # Calculating the names of maximum ordered vanilla and chocolate cakes in one period
    chocolate_dict = {}
    vanilla_dict = {}
    for order in vanilla_content:
        name = order["name"]
        if name not in vanilla_dict:
            vanilla_dict[name] = 1
        else:
            vanilla_dict[name] += 1

    for order in chocolate_content:
        name = order["name"]
        if name not in chocolate_dict:
            chocolate_dict[name] = 1
        else:
            chocolate_dict[name] += 1

    if vanilla_dict == {}:
        print("Vanilla Dict is empty")
        max_vanilla_orders = "No Vanilla Cakes Ordered"
    else:
        max_vanilla_orders = max(vanilla_dict, key=vanilla_dict.get)
    if chocolate_dict == {}:
        print("Chocolate dict is empty")
        max_chocolate_orders = "No Chocolate Cakes Ordered"
    else:
        max_chocolate_orders = max(chocolate_dict, key=chocolate_dict.get)

    current_time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%dT%H:%M:%S.%f")
    # Declare the final calculated data for the data.json file
    final_data = {
        "num_vanilla_orders": num_vanilla_orders, 
        "num_chocolate_orders": num_chocolate_orders,
        "max_vanilla_orders": max_vanilla_orders, 
        "max_chocolate_orders": max_chocolate_orders, 
        "last_updated": current_time
    }


    # Writing updated data to json file
    with open(app_config["datastore"]["filename"], "w") as json_file:
        json_file.write(json.dumps(final_data))
    logger.debug(f"The statistics values updated with {json.dumps(final_data)}")

    logger.info("Period Processing has ended.")
    return NoContent, 201


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 
                    'interval', 
                    seconds=app_config['scheduler']['period_sec'])
    sched.start()


def get_stats():
    """Recieves a Cake Orders"""
    logger.info("Request has started")
    try:
        with open(app_config["datastore"]["filename"], "r") as json_file:
            content = json.loads(json_file.read())
            logger.debug(content)
    except FileNotFoundError:
        logger.error("Statistics do not exist")
        return 404

    logger.info("The request has completed")
    return content, 200



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100)
