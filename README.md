# Icinga2 Plugin with RequetsManager module and Cache/Redis

Lib description

### Python Pip's used:
***
* Redis (_**Key** => **Val** DB stockage dans le RAM_)
* Hiredis (_**C** Interface pour Redis_)
* EasySNMP (_Net-SNMP lib **Python** implementation en **Cython**_)
* Nagiosplugin (_Nagios plugin lib pour **Python**_)

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

* [Check Disk I/O](#check_disk_io) (checking disk input/output)
* check_disk_load (checking machine load)
* check_linux_cpu (checking CPU on linux Machines)
* ...

### Plugins

##### Default Params applied to all plugins

    -H - hostname/IP
    -p - Port number (default: 161)
    -C - Community (default: bornan)
    -v - Version (default: 2)
    -c - Critical value (default: 90)
    -w - Warning value (default: 80)

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

Copyright (c) 2016 Aurimas NAVICKAS All Rights Reserved.
