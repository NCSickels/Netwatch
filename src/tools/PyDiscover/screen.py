import signal
import threading
import os
import sys

# from ifaces import *
from data_al import DataAL, data_access, _data_reply, _data_request, _data_unique
from constants import SMODE_REPLY, SMODE_REQUEST, SMODE_HELP, SMODE_HOST


class WinSize:
    def __init__(self):
        self.ws_col = 0
        self.ws_row = 0


win_sz = WinSize()

screen = threading.Thread()
keys = threading.Thread()
sniffer = threading.Thread()
injection = threading.Thread()


def init_screen():
    global scroll, smode
    scroll = 0
    smode = SMODE_HOST

    signal.signal(signal.SIGINT, sighandler)
    signal.signal(signal.SIGTERM, sighandler)


def sighandler(signum):
    print("Exiting...")
    exit(0)


def scroll_limit():
    current_data_mode = DataAL()

    if smode == SMODE_REPLY:
        current_data_mode = _data_reply
    elif smode == SMODE_REQUEST:
        current_data_mode = _data_request
    elif smode == SMODE_HOST:
        current_data_mode = _data_unique
    elif smode == SMODE_HELP:
        current_data_mode = _data_unique
    else:
        return
    return current_data_mode.hosts_count() - scroll


def read_key():
    global scroll, smode, oldmode, win_sz

    ch = sys.stdin.read(1)

    # Check for arrow keys
    if ch == '\x1b':
        ch = sys.stdin.read(1)
        if ch == '[':
            ch = sys.stdin.read(1)
            if ch == 'B':
                ch = 'j'
            elif ch == 'A':
                ch = 'k'

    # Scroll up
    if ch == 'k':
        if scroll > 0:
            scroll -= 1
    # Scroll down
    elif ch == 'j':
        if scroll_limit() > 1:
            scroll += 1
    # Scroll page up
    elif ch == ',':
        for _ in range(win_sz.ws_row - 7):
            if scroll > 0:
                scroll -= 1
    # Scroll page down
    elif ch == '.':
        for _ in range(win_sz.ws_row - 7):
            if scroll_limit() > 1:
                scroll += 1
    # Show requests view
    elif ch == 'r':
        smode = SMODE_REQUEST
        scroll = 0
    # Show replies view
    elif ch == 'a':
        smode = SMODE_REPLY
        scroll = 0
    # Show unique hosts view
    elif ch == 'u':
        smode = SMODE_HOST
        scroll = 0
    # Quit
    elif ch == 'q':
        if smode == SMODE_HELP:
            smode = oldmode
        else:
            sighandler(0)
    # Show help screen
    elif ch == 'h':
        if smode != SMODE_HELP:
            oldmode = smode
            smode = SMODE_HELP
            scroll = 0

    print_screen()


def print_screen():
    global win_sz

    # Get Console Size
    try:
        size = os.get_terminal_size(0)
        win_sz.ws_row = size.lines
        win_sz.ws_col = size.columns
    except OSError:
        win_sz.ws_row = 24
        win_sz.ws_col = 80

    # Flush and print screen
    sys.stderr.write("\33[1;1H")
    with data_access:
        fill_screen()
    sys.stderr.write("\33[J")
    sys.stdout.flush()


def print_status_header():
    global smode, current_network, win_sz

    current_smode = None

    if smode == SMODE_REPLY:
        current_smode = "ARP Reply"
    elif smode == SMODE_REQUEST:
        current_smode = "ARP Request"
    elif smode == SMODE_HOST:
        current_smode = "Unique Hosts"
    elif smode == SMODE_HELP:
        current_smode = "Help"

    line = f' Currently scanning: ' + \
        f'{current_network}   |   Screen View: {current_smode}'
    print(line, end='')

    # Fill with spaces
    for _ in range(len(line), win_sz.ws_col - 1):
        print(' ', end='')
    print()

    # Print blank line with spaces
    for _ in range(win_sz.ws_col - 1):
        print(' ', end='')
    print()


def fill_screen():
    current_data_mode = DataAL()

    if smode == SMODE_REPLY:
        current_data_mode = _data_reply
    elif smode == SMODE_REQUEST:
        current_data_mode = _data_request
    elif smode == SMODE_HOST:
        current_data_mode = _data_unique
    elif smode == SMODE_HELP:
        current_data_mode = _data_unique
    else:
        return

    print_status_header()
    current_data_mode.print_header(win_sz.ws_col)

    if smode != SMODE_HELP:
        x = 0
        current_data_mode.beginning_registry()
        while current_data_mode.current_registry() is not None:
            if x >= scroll:
                current_data_mode.print_line()
            current_data_mode.next_registry()
            x += 1

            if x >= (win_sz.ws_row + scroll) - 7:
                break
    elif smode == SMODE_HELP:
        print("\t  ______________________________________________  \n"
              "\t |                                              | \n"
              "\t |    \33[1mUsage Keys\33[0m                                | \n"
              "\t |     h: show this help screen                 | \n"
              "\t |     j: scroll down (or down arrow)           | \n"
              "\t |     k: scroll up   (or up arrow)             | \n"
              "\t |     .: scroll page up                        | \n"
              "\t |     ,: scroll page down                      | \n"
              "\t |     q: exit this screen or end               | \n"
              "\t |                                              | \n"
              "\t |    \33[1mScreen views\33[0m                              | \n"
              "\t |     a: show arp replies list                 | \n"
              "\t |     r: show arp requests list                | \n"
              "\t |     u: show unique hosts detected            | \n"
              "\t |                                              | \n"
              "\t  ----------------------------------------------  \n")
        for _ in range(25, win_sz.ws_row):
            print("\n")
