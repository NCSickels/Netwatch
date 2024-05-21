import time
from data_al import *
from oui import oui_table


known_mac_table = []


def string_cutter(string, size):
    return string[:size]


def search_vendor(mac):
    tmac = f'{mac[0]:02x}{mac[1]:02x}{mac[2]:02x}'

    # Convert mac prefix to upper
    tmac = tmac.upper()

    i = 0

    while oui_table[i]['prefix'] is not None:
        if oui_table[i]['prefix'] == tmac:
            return oui_table[i]['vendor']
        i += 1

    return 'Unknown vendor'


def load_known_mac_table(file_path):
    global known_mac_table

    # Open the file and read its contents
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print('ERROR: Unable to open the file.')
        return -1

    # Process each line
    for line in lines:
        line = line.strip()  # Remove leading/trailing whitespace
        if not line:  # Skip empty lines
            continue

        # Check if the line is a valid MAC address
        if len(line) < 12 + 2:  # MAC number + '/0' + '!' = 12+2 chars
            print(
                f'ERROR: No full MAC given in the file or empty line ({line})')
            time.sleep(5)
            if line:
                line = '?' + line[1:]  # Replace the first character with '?'
            else:
                break  # Skip the rest of the lines

        # Convert MAC to upper case
        line = line[:12].upper()

        # Convert all spaces and tabulator after MAC address into '\0'
        line = line.rstrip()  # Remove trailing spaces and tabs

        # Check if the line has a hostname
        if len(line) == 12:  # No hostname provided
            print(f'WARNING: No host name given in the file ({line})')
            time.sleep(5)
            line += '!'  # Append '!' as a placeholder

        # Add the processed line to the list
        known_mac_table.append(line)

    print('Parsing known MACs table completed.')
    return 0


def get_known_mac_hostname(mac_hostname):
    if len(mac_hostname) != 12:
        return None
    mac_hostname += 12
    while mac_hostname == '\0':
        mac_hostname += 1
    return mac_hostname


# find out known host name
def search_known_mac(mac):
    tmac = "".join(f"{x:02x}" for x in mac)

    # Convert mac to upper
    tmac = tmac.upper()

    i = 0

    while known_mac_table[i] is not None:
        if known_mac_table[i] == tmac:
            return get_known_mac_hostname(known_mac_table[i])
        i += 1

    return None


# First try find out known host name, otherwise use standard vendor
def search_mac(registry):
    registry.vendor = search_known_mac(registry.header.smac)

    if registry.vendor is None:
        registry.vendor = search_vendor(registry.header.smac)
        registry.vendor = 0  # unidentified host, vendor used
    else:
        registry.vendor = 1  # identified host, hostname used
