#!/usr/bin/env python3
#
#
#  ███╗   ██╗███╗   ███╗ █████╗ ██████╗
#  ████╗  ██║████╗ ████║██╔══██╗██╔══██╗
#  ██╔██╗ ██║██╔████╔██║███████║██████╔╝
#  ██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝
#  ██║ ╚████║██║ ╚═╝ ██║██║  ██║██║
#  ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
#
#  Netwatch v2.2.13: Nmap module
#  by: @NCSickels
#
import os
import sys
import copy
import ipaddress
import re
import tabulate
import time
import textwrap
from IPy import IP
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from modules.termutils import ColorConfig, LamePrint, TextOutput, constants
from modules.packagemanager import PackageManager
from logger import Logger
from config import settings

# TODO: Add support for nmap passthrough rather than hard coded commands


class Nmap:
    """ Nmap class for scanning hosts and generating reports. """

    SCAN_TYPES = {'default_scan': 'nmap -T4 -v -A -oN',
                  'quick_scan': 'nmap -T4 -F -v -oN',
                  'intense_scan': 'nmap -T4 -A -v -oN',
                  'vuln_scan': 'nmap -T4 -v -sV --script=vuln -oN'}

    def __init__(self):
        self.logger = Logger()
        self.package_manager = PackageManager("nmap")

    # TODO: Look at simplifying this method
    def check_nmap(self) -> bool:
        if not self.package_manager.find_package():
            self.logger.warning('Nmap not found.')
            response = self.prompt_input(
                'Would you like to install it now? [y/n]: ')
            if response in ['y', 'yes']:
                if (self.package_manager.install_package()):
                    self.logger.info('Nmap successfully installed.')
                    return True
                else:
                    self.logger.error('Failed to install Nmap.')
                    return False
            else:
                return False
        return True

    def prompt_input(self, prompt: str) -> str:
        while True:
            self.logger.info(prompt)
            user_input = input().lower()
            if user_input in ['y', 'n']:
                break
            else:
                self.logger.error('Unrecognized input. Please try again.')
        return user_input

    def scan(self, ip: any, file_name=None, scan_type='default_scan') -> None:
        if scan_type not in Nmap.SCAN_TYPES:
            self.logger.error('Invalid scan type.')
            return
        file_name = file_name if file_name else f'{ip}.xml'
        try:
            os.system(f'{Nmap.SCAN_TYPES[scan_type]} {file_name}.xml {ip}')
            self.logger.info('Scan completed.')
        except Exception as e:
            self.logger.error(f'An error occurred while scanning: {e}')
            return

        # try:
        #     print(scan_type)
        #     file_name = file_name if file_name else f'{ip}.xml'
        #     print(f"filename: {file_name}")


class NmapOutput:
    def __init__(self, xmlfiles):
        self.FilesFailedToImport = []
        self.FilesImported = []
        self.Hosts = {}
        self.Services = []
        self.Arguments = []
        self.helpers = NmapHelpers()
        self.color_config = ColorConfig()
        self.lame_print = LamePrint()
        # Import xml files
        self.parse_nmap_xml(xmlfiles)

    def parse_nmap_xml(self, xml_filenames: list) -> None:
        count = 0
        color_support = self.color_config.color_support()
        # Loop through all nmap xml files
        max_status_len = 0
        for xml_file_name in xml_filenames:
            xml_file_name = os.path.abspath(
                os.path.expanduser(xml_file_name))
            # print(f"Trying to open file at: {xml_file_name}")
            try:
                with open(xml_file_name, 'r') as f:
                    pass
            except Exception as e:
                print(f'Failed to open file: {e}')
            count += 1
            # Output stats
            if (xml_file_name in self.FilesImported):
                self.lame_print.hprint(
                    'Skipping previously imported file: ' + xml_file_name)
                continue
            sStatus = '\nLoading [%s of %s] %s' % (
                str(count), str(len(xml_filenames)), xml_file_name)
            if (color_support):
                sStatus = '\033[1;30m' + sStatus + '\033[1;m'
            # Pad short lines to overwrite previous text
            if (len(sStatus) < max_status_len):
                sStatus += " " * (max_status_len - len(sStatus))
            else:
                max_status_len = len(sStatus)
            if (count < len(xml_filenames)):
                self.lame_print.hprint(sStatus, end='\r')
            else:
                self.lame_print.hprint(sStatus)

            # Try to parse xml and record any failures
            nmap_xml = ""
            try:
                nmap_xml = ET.parse(xml_file_name)
            except:
                self.FilesFailedToImport.append(xml_file_name)
                continue
            # Record that file successfully loaded
            self.FilesImported.append(xml_file_name)
            # Find all hosts within xml file
            for xHost in nmap_xml.findall('.//host'):
                # Get IP address
                ipv4_element = xHost.find('address[@addrtype="ipv4"]')
                ipv6_element = xHost.find('address[@addrtype="ipv6"]')
                ip = None
                if (ipv4_element is not None):
                    ip = ipv4_element.get('addr')
                if (ipv6_element is not None):
                    ip = ipv6_element.get('addr')
                if (ip is None):
                    print('Host found without IPv4 or IPv6 address in ' +
                          xml_file_name + ', skipping host', file=sys.stderr)
                    continue
                # Add host to dictionary
                if ip not in self.Hosts:
                    self.Hosts[ip] = NmapHost(ip)
                cur_host = self.Hosts[ip]
                # Record what files host was found in
                if (xml_file_name not in cur_host.filesWithHost):
                    cur_host.filesWithHost.append(xml_file_name)

                # Attempt to get hostname
                try:
                    if (cur_host.hostname == '' or cur_host.hostname == ip):
                        # hostname will be in nmap xml if PTR (reverse lookup) record present
                        cur_host.hostname = xHost.find(
                            './/hostname').get('name')
                except:
                    cur_host.hostname = ip

                # Store host up status
                cur_host.alive = (xHost.find('status').get('state') == 'up')

                # Parse ports
                for xPort in xHost.findall('.//port'):
                    # Only parse open ports
                    if xPort.find('.//state').get('state') == 'open':
                        cur_port_id = int(xPort.get('portid'))
                        cur_protocol = xPort.get('protocol')
                        cur_service = ''
                        if (None != xPort.find('.//service')):
                            cur_service = xPort.find('.//service').get('name')
                        # Store port details
                        cur_host.add_port(
                            cur_protocol, cur_port_id, cur_service)
                        # Store service details in global variable
                        self.add_service(cur_service, ip, cur_port_id)
            # TODO: Ensure this is working correctly
            cmdline_args_element = nmap_xml.find('.//nmaprun')
            if cmdline_args_element is not None:
                cmdline_args = cmdline_args_element.get('args')
                if cmdline_args not in self.Arguments:
                    self.Arguments.append(cmdline_args)
                self.Arguments.append(cmdline_args)

    def add_service(self, service_name: str, ip: any, port: int) -> None:
        current_service = self.get_service(service_name)
        current_service_host = self.get_service_host(current_service, ip)
        current_service_host.ports = set(current_service_host.ports)
        current_service.ports = set(current_service.ports)
        current_service_host.ports.add(port)
        current_service.ports.add(port)

    def get_service_host(self, service: str, ip: any) -> None:
        for host in service.hosts:
            if host.ip == ip:
                return host
        new_service_host = NmapHost(ip)
        service.hosts.append(new_service_host)
        return new_service_host

    def get_service(self, service_name: str) -> None:
        for service in self.Services:
            if service.name == service_name:
                return service

        new_service = NmapService(service_name)
        self.Services.append(new_service)
        return new_service

    def get_host_dict(self, filters=None) -> dict:
        host_dict = {}
        for host in self.get_hosts(filters):
            host_dict[host.ip] = host
        return host_dict

    def get_hosts(self, filters=None) -> list:
        '''Returns an array of hosts that match filters'''
        if filters == None:
            filters = NmapFilters()

        matched_hosts = []
        host_ips = self.helpers.sort_ip_list(self.Hosts)
        for ip in host_ips:
            host = copy.deepcopy(self.Hosts[ip])
            if ((not host.alive) and filters.onlyAlive) or not filters.check_host(ip):
                continue
            matched = True
            # Check ports (if at least one filter is set)
            for protocol in constants.PROTOCOLS:
                for port in [port for port in host.ports if port.protocol == protocol]:
                    port.matched = True
                    if (
                        (filters.port_filter_set() and (filters.ports == [] or port.portId not in filters.ports)) or
                        (filters.service_filter_set() and (filters.services ==
                                                           [] or port.service not in filters.services))
                    ):
                        port.matched = False
                    if port.matched:
                        matched = True
            if filters.mustHavePorts and len(host.ports) == 0:
                matched = False
            # Dont check alive status as filter check has already failed
            if (matched == False and (filters.port_filter_set() or filters.service_filter_set() or filters.mustHavePorts)):
                continue
            if matched or (not filters.onlyAlive):
                matched_hosts.append(host)
            else:
                pass
        return matched_hosts

    def get_alive_hosts(self, filters=None) -> list:
        return [host.ip for host in self.get_hosts(filters) if host.alive]

    def get_services(self, filters=None) -> list:
        if filters == None:
            filters = NmapFilters()
        matched_services = []
        for service in self.Services:
            # Check if service matches filter
            if not (
                (filters.service_filter_set() and (filters.services == [] or service.name not in filters.services)) or
                (filters.port_filter_set() and (filters.ports == [] or not [port for port in service.ports if port in filters.ports])) or
                (filters.host_filter_set() and (filters.hosts == [] or not [
                 host for host in service.hosts if host in filters.hosts]))
            ):
                matched_services.append(service)
        return matched_services

    def get_nmap_cmdline(self, filters=None) -> list:
        return self.Arguments

    def generate_nmap_parse_xml(self, filename) -> None:
        # create the file structure
        xNmapParse = ET.Element('nmapparse')
        for ip in self.Hosts:
            cur_host = self.Hosts[ip]
            # Create host element
            xHost = ET.SubElement(xNmapParse, 'host')
            # Create status element
            xStatus = ET.SubElement(xHost, 'status')
            xStatus.set('state', 'up' if cur_host.alive else 'down')
            # Create address element
            xAddress = ET.SubElement(xHost, 'address')
            xAddress.set('addr', cur_host.ip)
            xAddress.set('addrtype', 'ipv4')
            # Create hostname element
            xHostnames = ET.SubElement(xHost, 'hostnames')
            if (cur_host.hostname != ip):
                xHostname = ET.SubElement(xHostnames, 'hostname')
                xHostname.set('name', cur_host.hostname)
            # Create ports element
            xPorts = ET.SubElement(xHost, 'ports')
            for port in cur_host.ports:
                xPort = ET.SubElement(xPorts, 'port')
                xPort.set('portid', str(port.portId))
                xPort.set('protocol', port.protocol)
                xState = ET.SubElement(xPort, 'state')
                xState.set('state', 'open')
                xService = ET.SubElement(xPort, 'service')
                xService.set('name', port.service)

        # create a new XML file with the results
        try:
            # Convert XML to string
            xml_data = ET.tostring(xNmapParse)
            # Format with indets
            bs = BeautifulSoup(xml_data, 'lxml-xml')
            xml_data = bs.prettify()
            # Write to file
            fhXml = open(filename, 'w')
            fhXml.write(str(xml_data))
            fhXml.close()
            self.lame_print.sprint('Combined file saved to: ' + filename)
        except Exception as ex:
            self.lame_print.eprint('Failed to combine files')
            self.lame_print.eprint(str(ex))

    def get_hosts_by_file(self, filters=None) -> dict:
        '''Returns a dictionary with filenames as ID's and an array of hosts'''
        file_host_dict = {}
        for host in self.get_hosts(filters=filters):
            for file in host.filesWithHost:
                if file not in file_host_dict:
                    file_host_dict[file] = []
                file_host_dict[file].append(host)
        return file_host_dict

    def get_hosts_within_file(self, file, filters=None) -> list:
        if (filters == None):
            filters = NmapFilters()
        return [host for host in self.get_hosts(filters=filters) if file in host.filesWithHost]

    def get_unique_port_ids(self, protocol=constants.PORT_OPT_COMBINED, filters=None, hosts=None) -> list:
        all_ports = set()
        if (hosts == None):
            hosts = self.get_hosts(filters)
        if (filters == None):
            filters = NmapFilters()
        for host in hosts:
            if protocol == constants.PORT_OPT_TCP:
                all_ports = all_ports.union(host.get_unique_port_ids(
                    constants.PORT_OPT_TCP, port_filter=filters.ports, service_filter=filters.services))
            elif protocol == constants.PORT_OPT_UDP:
                all_ports = all_ports.union(host.get_unique_port_ids(
                    constants.PORT_OPT_UDP, port_filter=filters.ports, service_filter=filters.services))
            else:
                all_ports = all_ports.union(host.get_unique_port_ids(
                    constants.PORT_OPT_TCP, port_filter=filters.ports, service_filter=filters.services))
                all_ports = all_ports.union(host.get_unique_port_ids(
                    constants.PORT_OPT_UDP, port_filter=filters.ports, service_filter=filters.services))
        return sorted(all_ports)


class NmapService:
    def __init__(self, name):
        self.name = name
        self.hosts = []
        self.ports = []


class NmapHost:
    def __init__(self, ip):
        self.ip = ip
        self.hostname = ''
        self.alive = False
        self.ports = []
        self.services = []
        self.matched = True  # Used for filtering
        self.filesWithHost = []  # List of nmap files host was found in

    def get_state(self) -> str:
        state = 'up'
        if not self.alive:
            state = 'down'
        return state

    def add_port(self, protocol: any, portId: any, service: any) -> None:
        self.add_service(service)
        for port in self.ports:
            if port.portId == portId and port.protocol == protocol:
                # Port already exists, check if service is blank and add if possible
                if (len(port.service.strip()) == 0):
                    port.service = service
                return
        # Add port if function hasn't already exited
        self.ports.append(NmapPort(protocol, portId, service))

    def add_service(self, service: any) -> None:
        if service not in self.services:
            self.services.append(service)

    def get_unique_port_ids(self, protocol='', port_filter=[], service_filter=[]) -> list:
        all_port_ids = []
        for port in self.ports:
            if (len(port_filter) > 0 and port.portId not in port_filter):
                continue
            if (len(service_filter) > 0 and port.service not in service_filter):
                continue
            if len(protocol) == 0 or port.protocol == protocol:
                all_port_ids.append(port.portId)

        unique_port_ids = set(all_port_ids)
        return sorted(unique_port_ids)

    def get_hostname(self) -> str:
        if self.hostname == self.ip:
            return ''
        return self.hostname


class NmapPort:
    def __init__(self, protocol, port, service):
        self.protocol = protocol
        self.portId = port
        self.service = service
        self.matched = True  # Used for filtering


class NmapFilters:
    def __init__(self, defaultBool=True):
        self.hosts = []
        self.ports = []
        self.services = []
        self.mustHavePorts = defaultBool
        self.onlyAlive = defaultBool

    # @property
    def check_filters_set(self) -> bool:
        return self.host_filter_set() or self.port_filter_set() or self.service_filter_set() or self.onlyAlive or self.mustHavePorts

    # @property
    def host_filter_set(self) -> bool:
        return len(self.hosts) > 0

    # @property
    def port_filter_set(self) -> bool:
        return len(self.ports) > 0

    # @property
    def service_filter_set(self) -> bool:
        return len(self.services) > 0

    def check_host(self, ip: any) -> bool:
        # Always return true if no filter is set
        if not self.host_filter_set():
            return True
        # Check if host matches any ips first
        matched = ip in [
            filter.filter for filter in self.hosts if filter.is_ip]
        # If no match found, check if host matches any network range
        if not matched:
            for filter in [filter for filter in self.hosts if filter.isNetwork]:
                if ipaddress.ip_address(ip) in ipaddress.ip_network(filter.filter):
                    matched = True
                    break
        return matched


class NmapHostFilter:
    def __init__(self, filter, is_ip):
        self.filter = filter
        self.is_ip = is_ip
        self.isNetwork = not is_ip


class NmapHelpers:
    """
    A class that provides helper methods for working with Nmap.

    Methods:
    - print_unique_ports: Prints the unique open ports for a given set of hosts.
    - get_unique_ports_output: Returns the unique open ports for a given set of hosts as a TextOutput object.
    - get_filters_string: Returns a string representation of the Nmap filters.
    - print_nmap_filters: Prints the Nmap filters.
    - get_host_list_output: Returns string representations of filtered hosts output.
    - print_hosts: Prints the filtered hosts output.
    - sort_ip_list: Sorts a list of IP addresses in ascending order.
    - print_import_summary: Prints a summary of the imported files.
    - get_service_list_output: Returns string representations of the service list.
    - print_service_list: Prints the service list.
    - execute_commands: Executes commands on the hosts that match the filters.
    - execute_command: Executes a command on a specific IP address.
    - print_alive_ips: Prints the list of alive IP addresses.
    - get_dir_files: Returns a list of files in a directory that match the specified filter.
    - string_to_host_filter: Converts a string representation of a host filter to a list of filters.
    """

    def __init__(self):
        self.lame_print = LamePrint()
        # self.text_output = TextOutput()

    def print_unique_ports(self, hosts: any, option=constants.PORT_OPT_DEFAULT, filters=None) -> str:
        ...


class NmapHelpers:
    def __init__(self):
        self.lame_print = LamePrint()
        self.logger = Logger()
        # self.text_output = TextOutput()

    def print_unique_ports(self, hosts: any, option=constants.PORT_OPT_DEFAULT, filters=None) -> str:
        text_output = self.get_unique_ports_output(
            hosts, option, filters=filters)
        text_output.print_to_console()

    def get_unique_ports_output(self, hosts: any, option=constants.PORT_OPT_DEFAULT, filters=None):
        if filters == None:
            filters = NmapFilters()
        tcp_ports = set()
        udp_ports = set()
        all_ports = set()
        for ip in hosts:
            host = hosts[ip]
            tcp_ports = tcp_ports.union(host.get_unique_port_ids(
                'tcp', port_filter=filters.ports, service_filter=filters.services))
            udp_ports = udp_ports.union(host.get_unique_port_ids(
                'udp', port_filter=filters.ports, service_filter=filters.services))
        all_ports = tcp_ports.union(udp_ports)

        output = TextOutput()
        output.add_humn(self.get_filters_string(filters))
        output.add_humn(self.lame_print.get_header(
            'Unique open port list (%s)' % (option)))
        if option == constants.PORT_OPT_DEFAULT:
            output.add_humn(self.lame_print.get_header('TCP:'))
            output.add_main(re.sub(r'[\[\] ]', '', str(sorted(tcp_ports))))
            output.add_humn(self.lame_print.get_header('UDP:'))
            output.add_main(re.sub(r'[\[\] ]', '', str(sorted(udp_ports))))
            output.add_humn(self.lame_print.get_header('Combined:'))
            output.add_main(re.sub(r'[\[\] ]', '', str(sorted(all_ports))))
        elif option == constants.PORT_OPT_TCP:
            output.add_main(re.sub(r'[\[\] ]', '', str(sorted(tcp_ports))))
        elif option == constants.PORT_OPT_UDP:
            output.add_main(re.sub(r'[\[\] ]', '', str(sorted(udp_ports))))
        elif option == constants.PORT_OPT_COMBINED:
            output.add_main(re.sub(r'[\[\] ]', '', str(sorted(all_ports))))
        return output

    def get_filters_string(self, filters: NmapFilters) -> str:
        filter_string = ""
        if filters.check_filters_set():
            filter_string += self.lame_print.get_header('Output filtered by:')
            if filters.host_filter_set():
                filter_string += ('Host filter [host_filter]: %s' % (
                    [filter.filter for filter in filters.hosts])) + os.linesep
            if filters.service_filter_set():
                filter_string += ('Service filter [service_filter]: %s' %
                                  (filters.services)) + os.linesep
            if filters.port_filter_set():
                filter_string += ('Port filter [port_filter]: %s' %
                                  (filters.ports)) + os.linesep
            if filters.mustHavePorts:
                filter_string += ('Must have ports filter [have_ports]: %s' % str(
                    filters.mustHavePorts)) + os.linesep
            if filters.onlyAlive:
                filter_string += ('Up filter [only_up]: %s' %
                                  str(filters.onlyAlive)) + os.linesep
        return filter_string

    def print_nmap_filters(self, filters: NmapFilters) -> None:
        filter_string = self.get_filters_string(filters)
        if (len(filter_string) > 0):
            self.hprint(filter_string)

    def get_host_list_output(self, nmap_output: any, include_ports=True, filters=None, include_hostname=False, is_table=False) -> str:
        """Returns string representations of filtered hosts output"""
        if filters == None:
            filters = NmapFilters()

        output = TextOutput()
        output.add_humn(self.get_filters_string(filters))
        output.add_humn(self.lame_print.get_header('Matched IP List'))

        headers = ['IP']
        if (include_hostname):
            headers.append('Hostname')
        for protocol in constants.PROTOCOLS:
            headers.append(protocol)

        table_rows = []
        # Get all hosts that are up and matched filters
        hosts_output = []
        for host in nmap_output.get_hosts(filters=filters):
            table_row = [host.ip]
            cur_host_output = [host.ip, '']

            if (include_hostname):
                if (host.hostname == host.ip):
                    table_row.append('')
                else:
                    table_row.append(host.hostname)
                    cur_host_output = [f"{host.ip} ({host.hostname})", '']

            for protocol in constants.PROTOCOLS:
                full_ports_string = ''
                for port in [port for port in host.ports if port.protocol == protocol]:
                    tmp_port_string = str(port.portId)
                    if (settings.PARSER_SETTINGS.color_supported and port.matched):
                        tmp_port_string = '\033[1;32m' + \
                            tmp_port_string + '\033[1;m'
                    if len(full_ports_string) > 0:
                        full_ports_string += ", "
                    full_ports_string += tmp_port_string
                cur_host_output[1] += '%s:[%s]  ' % (
                    protocol, full_ports_string)
                table_row.append(full_ports_string)
            hosts_output.append(cur_host_output)
            table_rows.append(table_row)

        if (is_table):
            output.add_main(tabulate.tabulate(
                table_rows, headers=headers, tablefmt='grid', maxheadercolwidths=[None, None, None, None], maxcolwidths=[None, None, 20, 20]))
        else:
            for host_data in hosts_output:
                if include_ports:
                    output.add_main(f'{host_data[0]}\t{host_data[1]}')
                    # output.add_main("%s\t%s" % (host_data[0], host_data[1]))
                else:
                    output.add_main(host_data[0])
        return output

    def print_hosts(self, nmap_output: any, include_ports=True, filters=None) -> None:
        text_output = self.get_host_list_output(
            nmap_output, include_ports=include_ports, filters=filters)
        text_output.print_to_console()

    def sort_ip_list(self, ip_list: list) -> list:
        ipl = [(IP(ip).int(), ip) for ip in ip_list]
        ipl.sort()
        return [ip[1] for ip in ipl]

    def print_import_summary(self, nmap_output: any, detailed=True) -> None:
        if (detailed):
            for file in nmap_output.FilesImported:
                self.lame_print.sprint('Successfully loaded ' + file)
        self.lame_print.sprint(os.linesep + 'Successfully loaded ' +
                               str(len(nmap_output.FilesImported)) + ' files')
        if len(nmap_output.FilesFailedToImport) > 0:
            self.lame_print.eprint('The following files failed to parse:')
            for file in nmap_output.FilesFailedToImport:
                self.lame_print.eprint('\t' + file)

    def get_service_list_output(self, nmap_output: any, filters=None, verbose=False, include_ports=True) -> str:
        services = nmap_output.get_services(filters)
        output = TextOutput()
        output.add_humn(self.lame_print.get_header('Service List'))
        first = True
        for service in services:
            if (verbose):
                if first:
                    first = False
                else:
                    output.add_main("")
            svc_string = service.name
            if (include_ports):
                svc_string += ' ' + str(sorted(service.ports))
            output.add_main(svc_string)
            if verbose:
                for host in service.hosts:
                    host_string = '  ' + host.ip
                    if (include_ports):
                        host_string += ' ' + str(sorted(host.ports))
                    output.add_main(host_string)
        return output

    def print_service_list(self, nmap_output: any, filters=None, verbose=False) -> None:
        text_output = self.get_service_list_output(
            nmap_output, filters=filters, verbose=verbose)
        text_output.print_to_console()

    def execute_commands(self, cmd: any, nmap_output: any, filters=None) -> None:
        if (filters == None):
            filters = NmapFilters()
        self.header('Running Commands')
        for host in nmap_output.get_hosts(filters):
            if len(host.ports) > 0:
                self.execute_command(cmd, host.ip)

    def execute_command(self, cmd: any, ip: any) -> None:
        cur_command = cmd + ' ' + ip
        self.lame_print.hprint("Running command: '%s'" % cur_command)
        process = Popen(cur_command, shell=True, stdout=PIPE)
        output = process.stdout.read()
        self.lame_print.hprint('Finished running command: %s' % cur_command)
        self.header("OUTPUT for '%s':" % cur_command)
        if output == '':
            print('<none>')
        else:
            print(output)
        print('')

    def print_alive_ips(self, nmap_output: any) -> None:
        self.header('Alive IP List')
        # Get all hosts that are up and matched filters
        tmp_parsed_hosts = nmap_output.get_alive_hosts()
        for ip in self.sort_ip_list(tmp_parsed_hosts):
            print("%s" % (ip))

    def get_dir_files(self, directory: any, filter='', recurse=False) -> list:
        all_files = []
        regex = re.compile(filter)
        if (recurse):
            for root, dirs, files in os.walk(directory):
                all_files.extend([os.path.join(root, file)
                                  for file in files if regex.match(os.path.join(root, file))])
        else:
            all_files.extend([os.path.join(directory, file) for file in os.listdir(
                directory) if regex.match(os.path.join(directory, file))])
        return all_files

    def string_to_host_filter(self, filter_string: any) -> list:
        host_filter = []
        raw_host_filter_string = filter_string
        # Remove any excess white space (start/end/between commas)
        # re.sub(r'[^\d\./,]', '', raw_host_filter_string)
        cur_host_filter_string = raw_host_filter_string.strip()
        # Split filter on comma, ignore empty entries and assign to filter
        tmp_host_filter = [ip.strip()
                           for ip in cur_host_filter_string.split(',') if len(ip) > 0]
        for cur_host_filter in tmp_host_filter:
            is_filename = False
            cur_filters = []
            # Check is specified filter is a file and attempt to load each line if it is
            if (os.path.isfile(cur_host_filter)):
                try:
                    is_filename = True
                    fhFile = open(cur_host_filter, 'r')
                    for line in fhFile:
                        if (len(line.strip()) > 0):
                            cur_filters.append(line.strip())
                    fhFile.close()
                except:
                    self.lame_print.eprint(
                        'Failed to load contents of: ' + cur_host_filter)
            else:
                cur_filters.append(cur_host_filter)

            for filter in cur_filters:
                valid_filter = False
                is_ip = False
                try:
                    ipaddress.ip_address(filter)
                    valid_filter = True
                    is_ip = True
                except ValueError:
                    pass

                try:
                    ipaddress.ip_network(filter)
                    valid_filter = True
                except ValueError:
                    pass
                if (valid_filter):
                    # TODO: Check this
                    host_filter.append(self.NmapHostFilter(filter, is_ip))
                else:
                    if (is_filename):
                        self.lame_print.eprint('Invalid host filter (within %s) option ignored: %s' % (
                            cur_host_filter, filter))
                    else:
                        self.lame_print.eprint(
                            'Invalid host filter option ignored: ' + filter)
        return host_filter

    def get_json_value(self, json_data: any, id: any) -> any:
        if id in json_data:
            return json_data[id]
        else:
            return ''

    def get_epoch(self) -> int:
        return int(time.time())

    def get_host_details(self, host: NmapHost) -> TextOutput:
        output = TextOutput()
        # Get overview
        output.add_humn(self.lame_print.get_header("Overview"))
        output.add_main('IP: %s' % host.ip)
        if (host.ip != host.hostname):
            output.add_main('Hostname: %s' % host.hostname)
        output.add_main("State: %s" % host.get_state())
        open_tcp = len(host.get_unique_port_ids(constants.PORT_OPT_TCP))
        open_udp = len(host.get_unique_port_ids(constants.PORT_OPT_UDP))
        output.add_main('TCP ports open: %s' % open_tcp)
        output.add_main('UDP ports open: %s' % open_udp)
        output.add_main('Total ports open: %s' % (open_tcp + open_udp))

        # Output port details
        output.add_humn(self.lame_print.get_header('Ports / Services'))
        port_table_headers = ['Port', 'Protocol', 'Service']
        output.add_main(tabulate.tabulate([[port.portId, port.protocol, port.service]
                                          for port in host.ports], headers=port_table_headers, tablefmt='github'))

        # Output files found in
        output.add_humn(self.lame_print.get_header('Files Containing Host'))
        if (len(host.filesWithHost) == 0):
            output.add_error('Host not present within any files')
        else:
            for file in host.filesWithHost:
                output.add_main(file)

        return output

    def wrap_text(self, text: any, max_chars=50) -> str:
        return os.linesep.join(textwrap.wrap(text, max_chars))

    def get_nmap_files(self, fileOrDir: any, recurse=False) -> list:
        if not os.path.exists(fileOrDir):
            raise FileNotFoundError(
                f"No such file or directory: '{fileOrDir}'")
        if os.path.isdir(fileOrDir):
            return self.get_dir_files(fileOrDir, filter=r'.*\.xml$', recurse=recurse)
        else:
            return [fileOrDir]
