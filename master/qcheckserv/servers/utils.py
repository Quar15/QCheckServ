import copy

class ServerDataResponse():

    def __init__(self):
        self.values_cpu = []
        self.values_loadavg = []
        self.values_mem = []
        self.values_partitions = []
        self.values_bytes_received = []
        self.values_bytes_sent = []

    def __repr__(self):
        return f"ServerDataResponse<{self.values_cpu} | {self.values_loadavg} | {self.values_mem} | {self.values_partitions} | {self.values_bytes_received} | {self.values_bytes_sent}>"

    def append_value(self, value):
        if value == 'ERROR':
            self.values_cpu.append("ERROR")
            self.values_loadavg.append("ERROR")
            self.values_mem.append("ERROR")
            self.values_partitions.append([])
            self.values_bytes_received.append("ERROR")
            self.values_bytes_sent.append("ERROR")
        else:
            self.values_cpu.append(value.cpu_perc)
            self.values_loadavg.append(value.loadavg)
            self.values_mem.append(value.mem_perc)
            self.values_partitions.append(value.partitions)
            self.values_bytes_received.append(value.bytes_received / 1024 / 1024)
            self.values_bytes_sent.append(value.bytes_sent / 1024 / 1024)


    def try_to_fix_partitions_data(self):
        # @TODO: Dirty fix for partitions
        example_partition_data = []
        for partition in self.values_partitions:
            if partition != []:
                example_partition_data = copy.deepcopy(partition)
                break
        for i in range(len(example_partition_data)):
            example_partition_data[i]["usage_perc"] = "ERROR"
            example_partition_data[i]["used"] = "ERROR"
            example_partition_data[i]["total"] = "ERROR"
            example_partition_data[i]["inodes_free"] = "ERROR"
            example_partition_data[i]["inodes_files"] = "ERROR"
        
        for i in range(len(self.values_partitions)):
            if not self.values_partitions[i]:
                self.values_partitions[i] = example_partition_data