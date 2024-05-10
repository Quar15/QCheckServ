import os, psutil, datetime
from time import sleep
import socket, requests
import json
import logging
from dotenv import find_dotenv, load_dotenv


# Try to load .env
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path)

PROTOCOL = "http://" if os.getenv("QCHECKSERV_USE_HTTP") == 'true' else "https://"
MASTER_IP = os.getenv("QCHECKSERV_MASTER_IP")
LOG_FORMAT = os.getenv("QCHECKSERV_LOG_FORMAT")
LOG_PATH = os.getenv("QCHECKSERV_LOG_PATH")
SAVE_FILE_PATH = os.getenv("QCHECKSERV_SAVE_FILE_PATH")
env_repeats_after_send_failure = int(os.getenv("QCHECKSERV_REPEATS_AFTER_SEND_FAILURE"), 0)
REPEATS_AFTER_SEND_FAILURE = 0 if env_repeats_after_send_failure < 0 else env_repeats_after_send_failure
REPEAT_AFTER_SEND_FAILURE_TIMEOUT = int(os.getenv("QCHECKSERV_REPEAT_AFTER_SEND_FAILURE_TIMEOUT"))

LOG_LEVEL = logging.INFO
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
VERSION = 1

logger = logging.getLogger(__name__)

def gatherData():
    if os.path.exists(SAVE_FILE_PATH):
        with open(SAVE_FILE_PATH, "r+") as f:
            data = json.load(f)
    else:
        data = {}

    data['version'] = VERSION
    data['timestamp'] = datetime.datetime.now().strftime(DATETIME_FORMAT)
    data['hostname'] = socket.gethostname()
    data['cpu_perc'] = psutil.cpu_percent(4)
    data['loadavg'] = psutil.getloadavg()
    data['mem_perc'] = psutil.virtual_memory().percent
    data['partitions'] = []
    for partition in psutil.disk_partitions():
        data['partitions'].append({
            "mountpoint": partition.mountpoint, 
            "usage_perc": psutil.disk_usage(partition.mountpoint).percent
        })

    net_io_counters = psutil.net_io_counters()
    if 'last_bytes_received' in data and 'last_bytes_sent' in data:
        data['bytes_received'] = net_io_counters.bytes_recv - data['last_bytes_received']
        data['bytes_sent'] = net_io_counters.bytes_sent - data['last_bytes_sent']

    data['last_bytes_received'] = net_io_counters.bytes_recv
    data['last_bytes_sent'] = net_io_counters.bytes_sent
    
    return data


def saveData(data):
    with open(SAVE_FILE_PATH, "w") as f:
        json.dump(data, f, indent=4)


def sendData(data):
    repeat_counter = -1
    while repeat_counter < REPEATS_AFTER_SEND_FAILURE:
        repeat_counter += 1
        url = PROTOCOL + MASTER_IP + "/api/gather"
        try:
            response = requests.post(url, json=data)
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to master node ({url})")
            sleep(REPEAT_AFTER_SEND_FAILURE_TIMEOUT)
            continue
        
        if response.status_code == 200:
            logger.debug(f"Request success")
        else:
            logger.error(f"Request failed ({url} returned {response.status_code})")
            sleep(REPEAT_AFTER_SEND_FAILURE_TIMEOUT)


def main():
    data = gatherData()
    if 'bytes_received' in data:
        logger.debug(f"{(data['bytes_received'] / 1024 / 1024):.2f} MB | {(data['bytes_sent'] / 1024 / 1024):.2f} MB")
    saveData(data)
    sendData(data)


if __name__ == "__main__":
    logging.basicConfig(filename=LOG_PATH, level=LOG_LEVEL, format=LOG_FORMAT)
    main()