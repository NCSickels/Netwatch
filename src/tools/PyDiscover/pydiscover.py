import os
import sys
import threading
import time
import signal
import subprocess
import re
import argparse
from scapy.all import *
# from ifaces import inject_init
# from data_reply import _data_reply
# from data_request import _data_request
# from data_unique import _data_unique
# from screen import init_screen, print_screen, read_key

RPATH = "{}/.pydiscover/ranges"
FPATH = "{}/.pydiscover/fastips"

# Last octect of ips scaned in fast mode
# Add new addr if needed here
fast_ips = []
dfast_ips = ["1", "2", "100", "200", "254", None]

# Common local networks to scan
# Add new networks if needed here
common_net = []
dcommon_net = [
    "192.168.0.0/16",
    "172.16.0.0/16",
    "172.26.0.0/16",
    "172.27.0.0/16",
    "172.17.0.0/16",
    "172.18.0.0/16",
    "172.19.0.0/16",
    "172.20.0.0/16",
    "172.21.0.0/16",
    "172.22.0.0/16",
    "172.23.0.0/16",
    "172.24.0.0/16",
    "172.25.0.0/16",
    "172.28.0.0/16",
    "172.29.0.0/16",
    "172.30.0.0/16",
    "172.31.0.0/16",
    "10.0.0.0/8",
    None
]

injection = None
sniffer = None
screen = None
keys = None

# Command line flags
flag_fast_mode = False
flag_repeat_scan = False
flag_network_octect = False
flag_supress_sleep = False
flag_ignore_files = False
flag_auto_scan = False
flag_sleep_time = 99


class PyDiscover:
    def __init__(self):
        self.flag_passive_mode = False
        self.parsable_output = False
        self.continue_listening = False
        self.dataos = {}
        self.interfaces = show_interfaces(resolve_mac=True)
        self.ifaces_data = IFACES.data

    def run(self):
        parser = argparse.ArgumentParser(
            usage='{prog} [-i device] [-r range | -l file | -p] [-m file] [-F filter] [-s time] [-c count] [-n node] [-dfPLNS]\n')

        parser.add_argument('-i', type=str, dest='device',
                            help='Set the interface')

        parser.add_argument('-p', dest='passive', action='store_true',
                            help='Enable passive mode')
        parser.add_argument('-s', dest='sleeptime',
                            type=int, help='Set sleep time')
        parser.add_argument('-S', dest='suppress', action='store_true',
                            help='Enable sleep suppression')
        parser.add_argument(
            '-c', dest='count', type=int, help='Set no. of times to repeat the scan')
        parser.add_argument('-n', dest='lastoctet',
                            type=int, help='Set last used octet')
        parser.add_argument('-r', dest='range', type=str,
                            help='Set the range to scan')
        parser.add_argument(
            '-l', dest='listfile', type=str, help='Scan ranges on the given file')
        parser.add_argument('-m', dest='macfile', type=str,
                            help='Scan MACs on the given file')
        parser.add_argument('-f', dest='fastmode',
                            action='store_true', help='Enable fast mode')
        parser.add_argument(
            '-F', dest='filter', type=str, help='Customize pcap filter expression (default: \'arp\')')
        parser.add_argument('-d', dest='ignorehome', action='store_true',
                            help='Ignore home config files')
        parser.add_argument('-P', dest='parsable', action='store_true',
                            help='Produces parsable output (vs interactive screen)')
        parser.add_argument('-N', dest='noheader', action='store_true',
                            help='Do not print header under parsable mode')
        parser.add_argument('-L', dest='listening', action='store_true',
                            help='Continue to listen in parsable output mode after active scan is completed')

        args = parser.parse_args()

        match args:
            case args.device:  # Network device to use
                self.print_interface_details(self.ifaces_data)
                # self.dataos['interface'] = args.device
            case args.passive:  # Passive scan mode; do not scan anything, only sniff
                self.flag_passive_mode = True
            case args.sleeptime:  # Sleep time between scans
                flag_sleep_time = args.sleeptime
            case args.suppress:  # Suppress sleep time
                flag_supress_sleep = True
            case args.count:  # Number of times to repeat the scan
                flag_repeat_scan = args.count
            case args.lastoctet:  # Last octet of ips scaned in fast mode
                flag_network_octect = args.lastoctet
            case args.range:  # Range to scan
                self.dataos['source_ip'] = args.range
                flag_scan_range = True
            case args.listfile:  # File with ranges to scan
                plist = args.listfile
                flag_scan_list = True
            case args.macfile:  # File with MACs to scan
                mlist = args.macfile
            case args.fastmode:  # Fast mode
                flag_fast_mode = True
            case args.filter:  # Custom pcap filter
                self.dataos['pcap_filter'] = args.filter
            case args.ignorehome:  # Ignore home config files
                flag_ignore_files = True
            case args.parsable:  # Produce parsable output
                self.parsable_output = True
            case args.noheader:  # Do not print header under parsable mode
                no_parsable_header = True
            case args.listening:
                self.parsable_output = True
                self.continue_listening = True
            case _:
                parser.print_help()

        # # Check for uid 0 (root)
        # if os.getuid() != 0 and os.geteuid() != 0:
        #     print("You must be root to run this.")
        #     sys.exit(1)

        # # If no iface was specified, autoselect one. If none is found, exit
        # if self.dataos['interface'] is None:
        #     devices = None
        #     devices = scapy.findalldevs()
        #     if not devices:
        #         print("Couldn't find capture devices.")
        #         sys.exit(1)
        #     self.dataos['interface'] = devices[0]

        # # Check whether user config files are either disabled or can be found
        # if flag_ignore_files is False and 'HOME' not in os.environ:
        #     print("Couldn't figure out users home path (~). Please set the $HOME "
        #           "environment variable or specify -d to disable user configuration files.\n")
        #     sys.exit(1)

        # # Load user config files or set defaults
        # if flag_ignore_files is False:
        #     #     path = os.path.expanduser("~") + RPATH
        #     pass
        # else:
        #     common_net = dcommon_net
        #     fast_ips = dfast_ips

        # # Read range list given by user if specified
        # if flag_scan_list:
        #     with open(plist) as f:
        #         ranges = f.readlines()
        #         for r in ranges:
        #             common_net.append(r.strip())

        # # Read MAC list given by user if specified
        # if mlist:
        #     with open(mlist) as f:
        #         macs = f.readlines()
        #         for m in macs:
        #             common_net.append(m.strip())

        # # Initialize data layers and screen
        # inject_init(self.dataos['interface'])
        # _data_reply.init()
        # _data_request.init()
        # _data_unique.init()
        # init_screen()

        # # Initialize mutex
        # data_access = threading.Lock()

        # # If no mode was selected, enable auto scan
        # if not (flag_scan_range and self.flag_passive_mode):
        #     flag_auto_scan = True

        # # Start the execution
        # if self.parsable_output:
        #     if not no_parsable_header:
        #         pass
        #         # _data_unique.print_simple_header()
        # else:
        #     retsys = os.system("clear")
        #     if retsys != 0:
        #         print("clear system call failed")
        #     screen = threading.Thread(target=screen_refresh)
        #     keys = threading.Thread(target=keys_thread)
        #     screen.start()
        #     keys.start()

    def print_interface_details(ifaces):
        for iface_name, iface_info in ifaces.items():
            print(f'\nInterface: {iface_name}')
            print(f'Description: {iface_info.description}')
            print(f'IP Address: {iface_info.ip}')
            print(f'MAC Address: {iface_info.mac}')
            print(f'Broadcast: {iface_info.broadcast}')


def keys_thread():
    while 1 == 1:
        # read_key()
        pass


def screen_refresh():
    while 1 == 1:
        # print_screen()
        time.sleep(1)


def parsable_screen_refresh():
    pass


def main():
    pydiscover = PyDiscover()
    pydiscover.run()


if __name__ == "__main__":
    main()
