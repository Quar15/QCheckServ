import psutil
import socket
import json
import os
import datetime

SAVE_FILE_PATH = "./last_qcheckserv_data.json"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"
VERSION = 1

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


def main():
    data = gatherData()
    if 'bytes_received' in data:
        print(f"{(data['bytes_received'] / 1024 / 1024):.2f} MB | {(data['bytes_sent'] / 1024 / 1024):.2f} MB")
    saveData(data)


if __name__ == "__main__":
    main()