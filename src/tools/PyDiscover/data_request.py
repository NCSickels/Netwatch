from misc import search_mac
from data_al import DataRegistry, DataCounter, DataAL
from data_unique import _data_unique
from screen import win_sz
from constants import KNOWN_COLOR

request_first = DataRegistry()
request_current = DataRegistry()
request_last = DataRegistry()
request_count = DataCounter()


def request_init():
    request_first = None
    request_last = None


def request_beginning_registry():
    request_current = request_first


def request_next_registry():
    request_current = request_current.next


def request_current_registry():
    return request_current


def request_hosts_count():
    return request_count.hosts


blank = ' '


def request_print_line(request_current, win_sz):
    # Initialize line and tline
    line = " "
    tline = " "

    # Get source IP
    tline = f"{request_current.sip} "
    line += tline

    # Fill with spaces
    while len(line) < 17:
        line += " "

    # Get source MAC
    tline = f"{request_current.header.smac[0]:02x}:{request_current.header.smac[1]:02x}:{request_current.header.smac[2]:02x}:{
        request_current.header.smac[3]:02x}:{request_current.header.smac[4]:02x}:{request_current.header.smac[5]:02x}   "
    line += tline

    # Get destination IP
    tline = f"{request_current.dip}"
    line += tline

    # Fill with spaces
    while len(line) < 54:
        line += " "

    # Count, Length & Vendor
    tline = f"{request_current.count:5d}"
    line += tline

    # Fill again with spaces and cut the string to fit width
    while len(line) < win_sz.ws_col - 1 and len(line) < len(line) - 1:
        line += " "
    line = line[:win_sz.ws_col - 1]

    # Print host highlighted if its known
    if request_current.focused == 0:
        print(line)
    else:
        print(KNOWN_COLOR, line)


def request_add_registry(registry):
    i = 0

    _data_unique.add_registry(registry)

    if request_first is None:
        request_count.hosts += 1
        search_mac(registry)

        request_first = registry
        request_last = registry
    else:
        tmp_request = DataRegistry()
        tmp_request = request_first

        while tmp_request is not None and i != 1:
            if tmp_request.sip == registry.sip and tmp_request.dip == registry.dip and tmp_request.header.smac[:6] == registry.header.smac[:6]:
                tmp_request.count += 1
                tmp_request.header.length += registry.header.length

                i = 1
            tmp_request = tmp_request.next
        if i != 1:
            request_count.hosts += 1
            search_mac(registry)

            request_last.next = registry
            request_last = registry
    request_count.packets += 1
    request_count.length += registry.header.length


def request_print_header_summary(width, request_count):
    line = f" {request_count['packets']} Captured ARP Request packets, from {
        request_count['hosts']} hosts.   Total size: {request_count['length']}"
    print(line, end="")

    # Fill with spaces
    for j in range(len(line), width - 1):
        print(" ", end="")
    print()


def request_print_header(width, request_count):
    request_print_header_summary(width, request_count)
    print(" _____________________________________________________________________________")
    print("   IP            At MAC Address      Requests IP      Count")
    print(" -----------------------------------------------------------------------------")


_data_request = DataAL(
    request_init, request_beginning_registry, request_next_registry, request_current_registry, request_print_line, request_print_header, request_add_registry, request_hosts_count, request_print_header_summary)
