<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD029 -->

# Netwatch - Automated Attack Framework

<p align="center">

<!-- ![Netwatch Temporary Banner](.assets/netwatch-banner.jpg) -->
<img src=".assets/netwatch-banner.jpg" alt="Netwatch Temporary Banner" width="100%">

![Static Badge](https://img.shields.io/badge/Platform-Kali-blue?style=plastic&logo=kalilinux&logoSize=auto)
![Static Badge](https://img.shields.io/badge/Platform-Ubuntu-blue?style=plastic&logo=ubuntu&logoSize=auto)
[![Static Badge](https://img.shields.io/badge/Python%203.12+-FFDE57?style=plastic&label=Requirement&link=https%3A%2F%2Fwww.python.org%2Fdownloads)](https://www.python.org/downloads)
![Static Badge](https://img.shields.io/badge/Bash-white?style=plastic&logo=gnubash&logoColor=grey)
![Static Badge](https://img.shields.io/badge/Docker-blue?style=plastic&logo=docker&logoColor=white)

</p>

## Table of Contents

## Features

### Automated HackTheBox & TryHackMe Basic Initial Enumeration

### Netbreach - Breach Searching Tool

Netbreach is a breach searching tool that allows you to search for breaches using the various breach APIs or by using a local breach database.

#### Usage

```bash
> python netbreach.py --help

===================================================================================
     ███╗   ██╗███████╗████████╗██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗
     ████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║
     ██╔██╗ ██║█████╗     ██║   ██████╔╝██████╔╝█████╗  ███████║██║     ███████║
     ██║╚██╗██║██╔══╝     ██║   ██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║
     ██║ ╚████║███████╗   ██║   ██████╔╝██║  ██║███████╗██║  ██║╚██████╗██║  ██║
     ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
===================================================================================
    v{0.1.0}                                      Noah Sickels (@NCSickels)
===================================================================================

usage: netbreach.py [-h] [-d DATABASE] [-k KEYWORD] [-n NUMBER] [-o OUTPUT] [-p PROXY]

options:
  -h, --help            show this help message and exit
  -d DATABASE, --database DATABASE
                        Database used for the search (ProxyNova or LocalFile)
  -k KEYWORD, --keyword KEYWORD
                        Keyword (user/domain/pass) to search for leaks in the DB
  -n NUMBER, --number NUMBER
                        Number of results to show (default is 20)
  -o OUTPUT, --output OUTPUT
                        Save the results as json or txt into a file
  -p PROXY, --proxy PROXY
                        Set HTTP/S proxy (like http://localhost:8080)
```

### Nmap Scan Parser

Command-line Nmap XML parser. Accepts an Nmap XML file and allows you to iterate through the data and extract information from the scan.

#### Usage

```bash
> nmap-parse --help
Usage: nmap-parse.py [options] [list of nmap xml files or directories containing xml files]

Options:
-h, --help            show this help message and exit
-p PORTS, --port=PORTS
      Optional port filter argument e.g. 80 or 80,443
--service=SVCFILTER   Optional service filter argument e.g. http or ntp,http
      (only used in conjunction with -s)
-e CMD, --exec=CMD    Script or tool to run on each IP remaining after port
      filter is applied. IP will be appended to end of
      script command line
-l, --iplist          Print plain list of matching IPs
-a, --alive-hosts     Print plain list of all alive IPs
-s, --service-list     Also print list of unique services with names
-S, --host-summary    Show summary of scanned/alive hosts
-v, --verbose         Verbose service list
-u, --unique-ports     Print list of unique open ports
-R, --raw             Only print raw output (no headers)
-r, --recurse         Recurse subdirectories if directory provided for nmap
      files
-i, --interactive     Enter interactive shell
-c COMBINE, --combine=COMBINE
      Combine all input files into single nmap-parse
      compatible xml file
-V, --version         Print version info
```

##### Example

**Command:**

```bash
> python nmap_parse.py ../examples/scan1.xml
```

**Output:**

```plaintext
Loading [1 of 1] examples/scan1.xml
Successfully loaded 1 files

IP and Port List
----------------
74.207.244.221[scanme.nmap.org] [22, 80]

Unique Open Ports List (default)
----------------------

TCP:
----
22, 80

UDP:
----

Combined:
---------
22, 80

Summary
-------
Total hosts: 1
Alive hosts: 1
```

#### Flags

Available flags for the Nmap Parser are as follows:

* **-h (help)**
  * Displays help information
* **-l (list ips)**
  * Lists all IP addresses and ports if the host matches the specified port and/or service filter
* **-p / --ports [comma seperated ports]**
  * Filters output for **-l and -e** to only include hosts which have one or more specified ports open
* **--service [comma seperated services**
  * Filters output for **-l and -e** to only include hosts which have one or more specified services open (e.g. http/telnet/ftp)
* **-e / --exec**
  * Executes the specified command against each IP that matches filter in the format *'[exec_command] [ip_address]'*
* **-a / --alive-hosts**
  * Prints all IP addresses with a status of 'up' within the nmap XML files
* **-s / --service-list**
  * Prints list of all unique services identified as well as all ports the service was found on
  * Includes host information when used in conjuction with verbose flag '-v'
* **-S / --host-summary**
  * Prints total scanned and active hosts
* **-v / --verbose**
  * Includes relevant IP's within service list output **(-s / --service-list)**
* **-u / --unique-ports**
  * Prints the list of unique TCP and UDP ports. Also outputs a combined list containing all unique ports regardless of protocol
* **-R / --raw**
  * When set, no headers will be output, only the raw output will be printed to console
* **-i / --interactive**
  * Begin interactive session, see below
* **-c / --combine**
  * Will combine all nmap XML files into one single nmap-parse compatible XML file
  * When dealing with tens/hundreds of nmap files, consolidation into a single file significantly improves nmap-parse's performance

#### Interactive Mode

Interactive mode allows you to manually filter through different aspects of the provided input files.

##### Example

**Command:**

```bash
> python nmap_parse.py ../examples/scan1.xml -i
```

**Output:**

```plaintext
Loading [1 of 1] /tmp/example.xml
Successfully loaded 1 files
-----------------------------------------------------------

 /$$   /$$                                             
| $$$ | $$                                             
| $$$$| $$ /$$$$$$/$$$$   /$$$$$$   /$$$$$$            
| $$ $$ $$| $$_  $$_  $$ |____  $$ /$$__  $$           
| $$  $$$$| $$ \ $$ \ $$  /$$$$$$$| $$  \ $$           
| $$\  $$$| $$ | $$ | $$ /$$__  $$| $$  | $$           
| $$ \  $$| $$ | $$ | $$|  $$$$$$$| $$$$$$$/           
|__/  \__/|__/ |__/ |__/ \_______/| $$____/            
                                  | $$                 
                                  | $$                 
                                  |__/                 
       /$$$$$$$                                        
      | $$__  $$                                       
      | $$  \ $$ /$$$$$$   /$$$$$$   /$$$$$$$  /$$$$$$ 
      | $$$$$$$/|____  $$ /$$__  $$ /$$_____/ /$$__  $$
      | $$____/  /$$$$$$$| $$  \__/|  $$$$$$ | $$$$$$$$
      | $$      /$$__  $$| $$       \____  $$| $$_____/
      | $$     |  $$$$$$$| $$       /$$$$$$$/|  $$$$$$$
      |__/      \_______/|__/      |_______/  \_______/
 -----------------------------------------------------------

Welcome to nmap parse! Type ? to list commands
Tip: You can send output to clipboard using the redirect '>' operator without a filename

nmap-parse ~#  help

Documented commands (type help <topic>):

Nmap Commands
=============
alive_hosts  list  ports  scanned_hosts  set  show  unset

Other
=====
alias  exit  history  macro  pyscript  shell    
edit   help  load     py     quit      shortcuts


nmap-parse ~# 
```

#### Available Commands

##### `show options`

All available user configuration options:

```plaintext
nmap-parse ~# show options

| Setting        | Type   | Value   | Description                                                                       |
|----------------|--------|---------|-----------------------------------------------------------------------------------|
| service_filter | string |         | Comma seperated list of services to show, e.g. "http,ntp"                         |
| port_filter    | string |         | Comma seperated list of ports to show, e.g. "80,123"                              |
| host_filter    | string |         | Comma seperated list of hosts/subnets to show, e.g. "127.0.0.1,10.0.0.0/24"       |
| have_ports     | bool   | True    | When enabled, hosts with no open ports are excluded from output  [ True / False ] |
| include_ports  | bool   | True    | Toggles whether ports are included in 'list/services' output  [ True / False ]    |
| verbose        | bool   | False   | Shows verbose service information  [ True / False ]                               |
| raw            | bool   | False   | Shows raw output (no headings)  [ True / False ]                                  |

```

##### `set [option] [value]`

This command allows you to set the value of a specific option. Tab completion is supported for service and port filters.

```plaintext
nmap-parse ~# set host_filter 74.207.244.221 
Set [host_filter] ==> '74.207.244.221'
```

##### `unset [option]`

This command is used to unset a specific option.

```plaintext
nmap-parse ~# unset host_filter 
Set [host_filter] ==> ''
```

##### `list`

This command works similarly to the `-l` and `--iplist` flags. It lists all IP addresses and ports if the host matches the specified port and/or service filter.

**Command:**

```plaintext
nmap-parse ~# list

Matched IP List
---------------
74.207.244.221 (scanme.nmap.org) tcp:[22, 80] udp:[]
```

##### `alive_hosts`

This command works similarly to the `-a` and `--alive-hosts` flags. It prints all IP addresses with a status of 'up' within the nmap XML files.

**Command:**

```plaintext
nmap-parse ~# alive_hosts

Alive Hosts
-----------
74.207.244.221
```

##### `ports`

By default, this command will list all unique TCP and UDP ports as well as a combined list of all unique ports regardless of protocol.

**Command:**

```plaintext
nmap-parse ~# ports

Unique Open Ports List
----------------------

TCP:
----
22, 80

UDP:
----

Combined:
---------
22, 80
```

##### `scanned_hosts`

This command lists all IP addresses that were scanned regardless of whether they were up or down.

**Command:**

```plaintext
nmap-parse ~# scanned_hosts

Scanned Hosts
-------------
74.207.244.221
```

### Custom Colorized Logger Wrapper

Tailored colorized logger for Python scripts. Allows for easy logging of information, warnings, errors, and debug messages with color coding.

## Roadmap

* Web based front end.
* Feroxbuster
* jok3r
* Expliot - IOT Pentesting Framework
* SEToolKit
* Caldera

## Known Issues

* Some longer scans can cause the Nmap Parser to produce a type error due to possible ANSI escape codes in the output.
* Some hosts with a large number of open ports can cause an issue with the "list" command in the Nmap Parser.
