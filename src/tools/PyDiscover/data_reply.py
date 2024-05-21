from data_al import DataRegistry, DataCounter
from screen import win_sz
from constants import KNOWN_COLOR

first_reply = DataRegistry()
current_reply = DataRegistry()
last_reply = DataRegistry()
reply_counter = DataCounter()


def reply_init():
    first_reply = None
    last_reply = None


def reply_beginning_registry():
    current_reply = first_reply


def reply_next_registry():
    current_reply = current_reply.next


def reply_current_registry():
    return current_reply


def reply_hosts_count():
    return reply_counter.hosts


blank = ' '


def reply_print_line():
    global current_reply

    line = " "
    tline = " "

    # Set IP
    tline += f"{current_reply.sip}"
    line += tline

    # Fill with spaces
    while len(line) < 17:
        line += blank

    # IP & MAC
    tline = f"{current_reply.header.smac[0]:02x}:{current_reply.header.smac[1]:02x}:{current_reply.header.smac[2]:02x}:{
        current_reply.header.smac[3]:02x}:{current_reply.header.smac[4]:02x}:{current_reply.header.smac[5]:02x}"
    line += tline

    # Count, Length & Vendor
    tline = f"{current_reply.count:5d} {
        current_reply.header.length:7d}  {current_reply.vendor}"
    line += tline

    # Fill again with spaces and cut the string to fit width
    while len(line) < win_sz.ws_col - 1 and len(line) < len(line) - 1:
        line += blank
    line = line[:win_sz.ws_col - 1]

    # Print host highlighted if its known
    if current_reply.focused == 0:
        print(line)
    else:
        print(KNOWN_COLOR, line)
