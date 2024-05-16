import threading

# Mutex for data access
data_access = threading.Lock()


# Holds each data type total counters
class DataCounter:
    def __init__(self):
        self.packets = 0  # Total packets
        self.hosts = 0    # Total hosts
        self.length = 0   # Total length


# Holds ethernet headers packet data
class PHeader:
    def __init__(self):
        self.smac = [0]*6     # Source MAC
        self.dmac = [0]*6     # Destination MAC
        self.length = 0       # Packet length


# Holds registry data
class DataRegistry:
    def __init__(self):
        self.header = PHeader()  # Ethernet data header
        self.sip = ""            # Source IP
        self.dip = ""            # Destination IP
        self.vendor = ""         # MAC vendor
        self.type = 0            # Packet type
        self.count = 0           # Total packets count
        self.tlength = 0         # Total packets length
        self.focused = ""        # Focused (colour / bold)
        self.next = None         # Next registry


# Holds data abstraction layer for data types
class DataAL:
    def __init__(self):
        self.init = None                                      # Init data
        self.beginning_registry = None                        # Go to 1st reg
        self.next_registry = None                             # Go to next reg
        self.current_registry = None                          # Get current reg
        self.print_line = None                                # Print reg line
        self.print_header = None                              # Print scr header
        self.add_registry = None                              # Add new registry
        self.hosts_count = None                               # Get hosts count
        self.print_simple_header = None                       # Print smp header


# Data abstraction layer instances
_data_reply = DataAL()
_data_request = DataAL()
_data_unique = DataAL()
