from scapy.all import Ether, ARP, sendp, sniff, conf, IFACES
import sys


# Function to get MAC address of interface
def get_mac(ifname):
    if sys.platform.startswith('win'):
        # Windows implementation
        try:
            # self.print_interface_details(self.ifaces_data)
            all_interfaces = IFACES.keys()
            interface_obj = IFACES.dev_from_name(ifname)
            if interface_obj:
                # Display interface details
                # print(f"Default Interface Name: {current_iface}")
                # print(f"Description: {interface_obj.description}")
                # print(f"MAC Address: {interface_obj.mac}")
                # print(f"IP Address: {interface_obj.ip}\n\n")
                # # print(f"Network Mask: {interface_obj.netmask}")
                return interface_obj.mac
            else:
                print(f"Interface '{ifname}' not found.")
        except Exception as e:
            print(f"Error getting MAC address: {str(e)}")
            sys.exit(1)
    else:
        pass
        # # Unix/Linux implementation


def inject_init(disp):
    try:
        # Open interface for injection
        inject = conf.L2socket(iface=disp)
    except Exception as e:
        print(f"Error opening interface: {str(e)}")
        sys.exit(1)

    get_mac(disp)


# Function to forge and inject ARP packet
def forge_arp(source_ip, dest_ip, ifname):
    arp = ARP(op=2, pdst=dest_ip, psrc=source_ip,
              hwdst=get_mac(ifname), hwsrc=get_mac(ifname))
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / arp
    sendp(packet, iface=ifname)


# Function to process packets
def process_packet(packet):
    if ARP in packet:
        print("ARP packet received")
        if packet[ARP].op == 1:  # ARP request
            print("ARP Request: ", packet[ARP].psrc, " -> ", packet[ARP].pdst)
        elif packet[ARP].op == 2:  # ARP reply
            print("ARP Reply: ", packet[ARP].psrc, " -> ", packet[ARP].pdst)


# Capture packets
def start_sniffer(ifname):
    def packet_handler(packet):
        process_packet(packet)

    sniff(ifname=ifname, prn=packet_handler, store=0)
