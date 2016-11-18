# Icinga2 Plugin with RequetsManager module and Cache/Redis

Icinga2 plugins package using Request Manager to manage requests to machines
and use Cache when possible thus to remove load on worker machine and 
reduce UDP requests quantity.

### Python Pip's used:
***
* Redis (_**Key** => **Val** DB Database using RAM to stock data_)
* Hiredis (_**C** Redis C implementation_)
* EasySNMP (_Net-SNMP lib created using **Cython**_)
* Nagiosplugin (_Nagios plugin **Python** lib_)

### Why EasySNMP
***
**Testing 4 Python libs:**
* _**EasySNMP**_
* _**NetSNMP**_
* _**PySNMP**_
* _Unix SNMP lib native Unix function called with os.popen as **NativeSNMP**_

#### Benchmark Tests
Tests were executed using same OIDs and SNMPWalk function.

Results in seconds (s):
</br>

| Times called   | EasySNMP       | NetSNMP        | PySNMP         | NativeSNMP    |
| :------------- | :------------- | :------------- | :------------- |:------------- |
| 1 x            | 0.013871s      | **0.003734s**  | 0.516798s      | 0.005819s     |
| 10 x           | 0.020231s      | **0.016021s**  | 4.788551s      | 0.058144s     |
| 100 x          | **0.053363s**  | 0.180546s      | 53.863760s     | 0.616921s     |
| 1 000 x        | **0.381411s**  | 1.931081s      | 3255.206666s   | 6.720697s     |
| 10 000 x       | **3.930478s**  | 18.342071s     | N/A            | 156.051447s   |


| Average Time for 1 req.  | EasySNMP       | NetSNMP        | PySNMP         | NativeSNMP    |
| :-------------           | :------------- | :------------- | :------------- |:------------- |
| Times called x 1         | 0.013871s      | **0.003734s**  | 0.516798s      | 0.005819s     |
| Times called x 10        | 0.002023s      | **0.001602s**  | 0.478855s      | 0.005814s     |
| Times called x 100       | **0.000534s**  | 0.001806s      | 0.538638s      | 0.006169s     |
| Times called x 1 000     | **0.000381s**  | 0.001931s      | 3.255207s      | 0.006721s     |
| Times called x 10 000    | **0.000393s**  | 0.001834s      | N/A            | 0.015605s     |
| ------------------------ | -------------- | -------------- | -------------- | ------------- |
| Summary of Average       | 0.003440s      | **0.002181s**  | 1.197375s      | 0.008026s     |

_EasySNMP manages very well big quantity of requests using single SNMP session._

### General Icinga2 plugin's Flow Diagram using RequestManager Module and Cache/Redis
***
![Diagrame d'une sonde](https://rawgit.com/aurimukas/icinga2_plugins/master/docs/img/sonde_diagram.svg)

#### Benchmark Tests using Icinga2 tasks load

Not done yet!!

# Icinga2 plugins

### Plugins List

* [Check Disk I/O](#user-content-check_disk_io) (checking disk input/output)
* [Check Interface Traffic](#user-content-check_interface_traffic) (Checking Network activity on selected Net Interface)
* [Check Load](#user-content-check_load) (Checking Machine Load)
* [Check Linux Memory]() (Checking Memory on Linux Machines)
* Check Alteon Memory (Check Memory on ALTEON Machines)
* Check Bintec Memory (Check Memory on BINTEC Machines)
* Check Cisco ASR Memory (Check Memory on CISCO ASR Machines)
* Check Cisco Memory (Check Memory on CISCO Machines)
* Check Cisco Nexus Memory (Check Memory on CISCO NEXUS Machines)
* Check Fortinet Memory (Check Memory on FORTINET Machines)
* Check H3C Memory (Check Memory on H3C Machines)
* Check Juniper Memory (Check Memory on JUNIPER Machines)
* Check Sun Memory (Check Memory on SUN Machines)
* Check Windows Memory (Check Memory on WINDOWS Machines)
* [Check Linux CPU](#user-content-check_linux_cpu) (checking CPU on linux Machines)
* [Check Sun CPU]() (Check CPU on SUN Machines)
* [Check Windows CPU]() (Check CPU on WINDOWS Machines)
* Check Juniper CPU (Check CPU on Juniper Machines)
* Check H3C CPU (Check CPU on H3C Machines)
* Check Fortinet CPU (Check CPU on FORTINET Machines)
* Check Fortinet5103 CPU (Check CPU on FORTINET5103 Machines)
* Check Cisco Nexus CPU (Check CPU on CISCO NEXUS Machines)
* Check Cisco ASR CPU (Check CPU on CISCO ASR Machines)
* Check Cisco ASA CPU (Check CPU on CISCO ASA Machines)
* Check Bintec CPU (Check CPU on BINTEC Machines)
* Check Alteon CPU (Check CPU on ALTEON Machines)
* ...

### Plugins

##### Default Params applied to all plugins

    -H - hostname/IP
    -p - Port number (default: 161)
    -C - Community (default: bornan)
    -v - Version (default: 2)
    -c - Critical value (default: 90)
    -w - Warning value (default: 80)
    -V - Verbose Level (default: 0, log print. action: count)

#### check_disk_io
___
Monitoring disk's I/O data.

##### Params to pass on function execution:
    -d - Disk to monitor label. a.e. sda, vda etc...
##### Calling a function example:
    $ python check_disk_io.py -H 127.0.0.1 -v 2c -c bornan -d sda -c 90 -w 80
##### Performance Data to Return:
    alert_ioread
    alert_iowrite
##### Successful Results:
    DISKIO OK - alert_ioread is 0 | alert_ioread=0.0;80.0;90.0 alert_iowrite=0.0;80.0;90.0
##### False Results:
    DISKIO UNKNOWN - Error while fetching Indexes. Label: vdd

#### check_interface_traffic
___
Monitoring machine's network activity on selected interface.
##### Params to pass on function execution:
    -d or --descr - Interface name to monitor. a.e. eth0, eth1 etc...
##### Calling a function example:
    $ python check_interface_traffic.py -H 127.0.0.1 -v 2c -c bornan -c 90 -w 80 -d eth0
##### Performance Data to Return:
    alert_traffic_in_percent
    alert_traffic_out_percent
    traffic_in_bps
    traffic_out_bps
##### Successful Results:
    INTERFACETRAFFIC OK - traffic_in_bps is 13.23 | alert_traffic_in_percent=0.0;80.0;90.0 alert_traffic_out_percent=0.0;80.0;90.0 traffic_in_bps=13.23 traffic_out_bps=13.7
##### False Results:
    INTERFACETRAFFIC UNKNOWN - Error while ...
    
#### check_linux_cpu
___
Monitoring Linux machine's CPU activity in %.

##### Params to pass on function execution:
    No params to pass
##### Calling a function example:
    $ python check_linux_cpu.py -H 127.0.0.1 -v 2c -c bornan -c 90 -w 80
##### Performance Data to Return:
    alert_cpu_percent
##### Successful Results:
    LINUXCPU OK - alert_cpu_percent is 0.75 | alert_cpu_percent=0.75;80.0;90.0
##### False Results:
    LINUXCPU UNKNOWN - Error while ...
    
#### check_load
___
Monitoring machine's load status.

##### Params to pass on function execution:
    No params to pass
##### Calling a function example:
    $ python check_load.py -H 127.0.0.1 -v 2c -c bornan -c 90 -w 80
##### Performance Data to Return:
    load_1
    alert_load_5
    load_15
##### Successful Results:
    SYSTEMLOAD OK - load_15 is 0.15 | alert_load_5=0.0;80.0;90.0 load_15=0.15 load_1=0.0
##### False Results:
    SYSTEMLOAD UNKNOWN - Error while ...

Copyright (c) 2016 Aurimas NAVICKAS All Rights Reserved.
