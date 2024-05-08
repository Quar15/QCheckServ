# QCheckServ
Version: 0.1.0

**NOTE**: Project is work in progress, all can change until version 1.0.0

*Quickly check servers status* - **QCheckServ** is dashboard and gatherers for resource usage of one or multiple servers. 

Each server gathers data about:
* CPU usage, 
* RAM usage, 
* load average, 
* storage usage (for each mountpoint), 
* network usage
* process list

every 5 minutes using **slave node** and sends it to **master node** database.

Then gathered data can be seen in **master node** dashboards.

## Features

* Slave Node
    * gathering resource usage info about server, containers and databases
    * sending them to master node
* Master Node
    * database that gathers info about resource usage
    * dashboards
        * servers list + server details dashboard
        * docker containers list + container details dashboard
        * databases list + database details dashboard
        * alerts list + ability to create own alerts