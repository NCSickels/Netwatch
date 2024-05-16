import time
import os
from data_al import DataRegistry, DataCounter, DataAL
from screen import sighandler
from pydiscover import parsable_output, continue_listening
from misc import search_mac
from constants import KNOWN_COLOR

first_unique = DataRegistry()
current_unique = DataRegistry()
last_unique = DataRegistry()
unique_count = DataCounter()


def unique_init():
    first_unique = None
    last_unique = None


def unique_beginning_registry():
    current_unique = first_unique


def unique_next_registry():
    current_unique = current_unique.next


def unique_current_registry():
    return current_unique


def unique_hosts_count():
    return unique_count.hosts


blank = ' '


def unique_print_line():
    line = " "
    tline = " "

    # Set IP
    tline = f"{current_unique.sip} "
    line += tline

    # Fill with spaces
    line = line.ljust(17)

    # IP & MAC
    tline = ":".join(
        f"{x:02x}" for x in current_unique.header.smac) + "  "
    line += tline

    # Count, Length & Vendor
    tline = f"{current_unique.count:5d} {
        current_unique.tlength:7d}  {current_unique.vendor}"
    line += tline

    # Fill again with spaces and cut the string to fit width
    line = line.ljust(os.get_terminal_size().columns - 1)

    # Print host highlighted if its known
    if current_unique.focused == 0:
        print(line)
    else:
        print(f"{KNOWN_COLOR}{line}")


def unique_add_registry(registry):
    i = 0

    if first_unique is None:
        new_data = registry.copy()

        unique_count.hosts += 1
        search_mac(new_data)

        global first_unique, last_unique, current_unique
        first_unique = new_data
        last_unique = new_data

        if parsable_output:
            current_unique = new_data

    else:
        tmp_registry = first_unique

        # Check for dupe packets
        while tmp_registry is not None and i != 1:
            if tmp_registry.sip == registry.sip and tmp_registry.header.smac == registry.header.smac:
                tmp_registry.count += 1
                tmp_registry.tlength += registry.header.length

                if parsable_output:
                    current_unique = None

                i = 1

            tmp_registry = tmp_registry.next

        # Add it if isn't dupe
        if i != 1:
            new_data = registry.copy()

            unique_count.hosts += 1
            search_mac(new_data)

            last_unique.hosts = new_data
            last_unique = new_data

            if parsable_output:
                current_unique = new_data

    unique_count.packets += 1
    unique_count.length += registry.header.length

    if parsable_output and current_unique is not None:
        unique_print_line()


def unique_print_header_summary(width):
    line = f" {unique_count.packets} Captured ARP Req/Rep packets, from {
        unique_count.hosts} hosts.   Total size: {unique_count.length}"
    print(line, end="")

    # Fill with spaces
    print(" " * (width - len(line) - 1))


def unique_print_simple_header():
    print(" _____________________________________________________________________________")
    print("   IP            At MAC Address     Count     Len  MAC Vendor / Hostname")
    print(" -----------------------------------------------------------------------------")


def unique_print_header(width):
    unique_print_header_summary(width)
    unique_print_simple_header()


_data_unique = DataAL(
    unique_init, unique_beginning_registry, unique_next_registry, unique_current_registry, unique_print_line, unique_print_header, unique_add_registry, unique_hosts_count, unique_print_header_summary)


def parsable_scan_end():
    time.sleep(1)

    print(f"\n-- Active scan competed, {unique_count.hosts} Hosts found.")

    if continue_listening:
        print("Continuing to listen passively.\n\n")
    else:
        print("\n")
        sighandler(0)
