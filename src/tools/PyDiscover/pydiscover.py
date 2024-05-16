import os
import sys
import threading
import time
import signal
import subprocess
import re
import argparse
from scapy.all import IFACES, conf
import scapy.interfaces
import winreg
from data_al import data_access
from ifaces import get_mac, inject_init, forge_arp
from screen import init_screen, print_screen, read_key


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

flag_supress_sleep = False
flag_ignore_files = False
flag_sleep_time = 99
flag_network_octet = 67
flag_repeat_scan = 1
flag_auto_scan = False


class PyDiscover:
    def __init__(self):
        self.flag_passive_mode = False
        self.parsable_output = False
        self.continue_listening = False
        self.dataos = {"interface": None,
                       "source_ip": None, "pcap_filter": "arp"}
        # self.interfaces = show_interfaces(resolve_mac=True)
        self.ifaces_data = IFACES.data

    def run(self):
        parser = argparse.ArgumentParser(
            usage='{prog} [-i device] [-r range | -l file | -p] [-m file] [-F filter] [-s time] [-c count] [-n node] [-dfPLNS]\n')

        parser.add_argument('-i', dest='device', help='Set the interface')
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

        if args.device:  # Network device to use
            self.dataos['interface'] = args.device
            # print(f'\n\nInterface: {args.device}')
        elif args.passive:  # Passive scan mode; do not scan anything, only sniff
            self.flag_passive_mode = True
        elif args.sleeptime:  # Sleep time between scans
            flag_sleep_time = args.sleeptime
        elif args.suppress:  # Suppress sleep time
            flag_supress_sleep = True
        elif args.count:  # Number of times to repeat the scan
            flag_repeat_scan = args.count
        elif args.lastoctet:  # Last octet of ips scaned in fast mode
            flag_network_octect = args.lastoctet
        elif args.range:  # Range to scan
            self.dataos['source_ip'] = args.range
            flag_scan_range = True
        elif args.listfile:  # File with ranges to scan
            plist = args.listfile
            flag_scan_list = True
        elif args.macfile:  # File with MACs to scan
            mlist = args.macfile
        elif args.fastmode:  # Fast mode
            flag_fast_mode = True
        elif args.filter:  # Custom pcap filter
            self.dataos['pcap_filter'] = args.filter
        elif args.ignorehome:  # Ignore home config files
            flag_ignore_files = True
        elif args.parsable:  # Produce parsable output
            self.parsable_output = True
        elif args.noheader:  # Do not print header under parsable mode
            no_parsable_header = True
        elif args.listening:
            self.parsable_output = True
            self.continue_listening = True
        else:
            parser.print_help()

        self.dataos['interface'] = conf.iface
        inject_init(self.dataos['interface'])
        print(f'Successfully initialized interface: ' +
              f'{self.dataos["interface"]}')

        init_screen()

    def inject_arp(self):
        if flag_auto_scan is False:
            # print('Injecting ARP packets...')
            self.scan_range(self.dataos['interface'], self.dataos['source_ip'])
        else:
            x = 0
            while common_net[x] is not None:
                # print(f'Scanning network: {common_net[x]}')
                self.scan_range(self.dataos['interface'], common_net[x])
                x += 1
        # Wait for last arp replies and mark as scan finished
        os.sleep(2)
        current_network = 'Finished!'

    def scan_net(disp, sip):
        fromip = f'{sip}.{flag_network_octet}'
        print(fromip)
        for x in range(flag_repeat_scan):
            if flag_fast_mode is False:
                for y in range(1, 255):
                    testip = f'{sip}.{y}'
                    forge_arp(fromip, testip, disp)

                    # Check sleep time suppression
                    if flag_supress_sleep is False:
                        time.sleep(flag_sleep_time / 1000)
                        # Sleep time
                    else:
                        time.sleep(0.1)
            else:
                j = 0
                while fast_ips[j] is not None:
                    testip = f'{sip}.{fast_ips[j]}'
                    forge_arp(fromip, testip, disp)
                    j += 1

                    # Check sleep time suppression
                    if flag_supress_sleep is False:
                        time.sleep(flag_sleep_time / 1000)
                        # Sleep time
                    else:
                        time.sleep(0.1)

            if flag_supress_sleep is True:
                if flag_sleep_time != 99:
                    time.sleep(flag_sleep_time / 1000)
                    # Sleep time
                else:
                    time.sleep(0.1)

    def scan_range(self, interface, sip):
        delimiters = ".,/"
        tnet = sip
        a, b, c, d, *aux = tnet.split(delimiters)

        if aux:
            e = int(aux[0])
        else:
            e = 24

        if a or b or c or d is None:
            e = -1
        else:
            for val in [a, b, c, d]:
                try:
                    k = int(val)
                    if k < 0 or k > 255:
                        e = -1
                        break
                except ValueError:
                    e = -1
                    break

        # Scan class C network
        if e == 24:
            net = f'{a}.{b}.{c}'
            current_network = f'{net}.0/{e}'
            self.scan_net(interface, net)
        elif e == 16:
            for x in range(0, 256):
                net = f'{a}.{b}.{x}'
                current_network = f'{a}.{b}.{x}.0/{e}'
                self.scan_net(interface, net)
                x += 1
        elif e == 8:
            for x in range(0, 256):
                for y in range(0, 256):
                    net = f'{a}.{x}.{y}'
                    current_network = f'{a}.{x}.{y}.0/{e}'
                    self.scan_net(interface, net)
                    y += 1
                x += 1
        else:
            print('ERROR: Network range must be 0.0.0.0/8, /16, or /24\n\n')
            # signalhandler(0)
            exit(0)


def keys_thread():
    while 1 == 1:
        read_key()
        pass


def screen_refresh():
    while 1 == 1:
        print_screen()
        time.sleep(1)


def main():
    pydiscover = PyDiscover()
    pydiscover.run()


if __name__ == "__main__":
    main()
