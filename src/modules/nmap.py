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
from modules.termutils import *
from modules.notify import *
from modules.packagemanager import *
from logger import *
from config import *


class Nmap:
    """ Nmap class for scanning hosts and generating reports. """

    SCAN_TYPES = {'default_scan': 'nmap -T4 -v -A -oN',
                  'quick_scan': 'nmap -T4 -F -v -oN',
                  'intense_scan': 'nmap -T4 -A -v -oN',
                  'vuln_scan': 'nmap -T4 -v -sV --script=vuln -oN'}

    def __init__(self):
        self.logger = Logger()
        self.packageManager = PackageManager("nmap")

    # TODO: Look at simplifying this method
    def checkForNmap(self) -> bool:
        if not self.packageManager.checkForPackage():
            self.logger.warning('Nmap not found.')
            response = self.promptForInput(
                'Would you like to install it now? [y/n]: ')
            if response in ['y', 'yes']:
                if (self.packageManager.installPackage()):
                    self.logger.info('Nmap successfully installed.')
                    return True
                else:
                    self.logger.error('Failed to install Nmap.')
                    return False
            else:
                return False
        return True

    def promptForInput(self, prompt: str) -> str:
        while True:
            self.logger.info(prompt)
            user_input = input().lower()
            if user_input in ['y', 'n']:
                break
            else:
                self.logger.error('Unrecognized input. Please try again.')
        return user_input

    def scan(self, ip: any, fileName=None, scanType='default_scan') -> None:
        if scanType not in Nmap.SCAN_TYPES:
            self.logger.error('Invalid scan type.')
            return
        fileName = fileName if fileName else f'{ip}.xml'
        try:
            os.system(f'{Nmap.SCAN_TYPES[scanType]} {fileName}.xml {ip}')
            self.logger.info(f'Scan completed.')
        except Exception as e:
            self.logger.error(f'An error occurred while scanning: {e}')
            return

        # try:
        #     print(scanType)
        #     fileName = fileName if fileName else f'{ip}.xml'
        #     print(f"filename: {fileName}")


class NmapOutput:
    def __init__(self, xmlFiles):
        self.FilesFailedToImport = []
        self.FilesImported = []
        self.Hosts = {}
        self.Services = []
        self.Arguments = []
        self.helpers = NmapHelpers()
        self.configColor = ColorConfig()
        self.lamePrint = LamePrint()
        # Import xml files
        self.parseNmapXmlFiles(xmlFiles)

    def parseNmapXmlFiles(self, nmapXmlFilenames: list) -> None:
        count = 0
        colorSupport = self.configColor.supportsColor()
        # Loop through all nmap xml files
        iMaxStatusLen = 0
        for nmapXmlFilename in nmapXmlFilenames:
            nmapXmlFilename = os.path.abspath(
                os.path.expanduser(nmapXmlFilename))
            # print(f"Trying to open file at: {nmapXmlFilename}")
            try:
                with open(nmapXmlFilename, 'r') as f:
                    pass
            except Exception as e:
                print(f'Failed to open file: {e}')
            count += 1
            # Output stats
            if (nmapXmlFilename in self.FilesImported):
                self.lamePrint.hprint(
                    'Skipping previously imported file: ' + nmapXmlFilename)
                continue
            sStatus = '\nLoading [%s of %s] %s' % (
                str(count), str(len(nmapXmlFilenames)), nmapXmlFilename)
            if (colorSupport):
                sStatus = '\033[1;30m' + sStatus + '\033[1;m'
            # Pad short lines to overwrite previous text
            if (len(sStatus) < iMaxStatusLen):
                sStatus += " " * (iMaxStatusLen - len(sStatus))
            else:
                iMaxStatusLen = len(sStatus)
            if (count < len(nmapXmlFilenames)):
                self.lamePrint.hprint(sStatus, end='\r')
            else:
                self.lamePrint.hprint(sStatus)

            # Try to parse xml and record any failures
            nmap_xml = ""
            try:
                nmap_xml = ET.parse(nmapXmlFilename)
            except:
                self.FilesFailedToImport.append(nmapXmlFilename)
                continue
            # Record that file successfully loaded
            self.FilesImported.append(nmapXmlFilename)
            # Find all hosts within xml file
            for xHost in nmap_xml.findall('.//host'):
                # Get IP address
                ipv4Element = xHost.find('address[@addrtype="ipv4"]')
                ipv6Element = xHost.find('address[@addrtype="ipv6"]')
                ip = None
                if (ipv4Element is not None):
                    ip = ipv4Element.get('addr')
                if (ipv6Element is not None):
                    ip = ipv6Element.get('addr')
                if (ip is None):
                    print('Host found without IPv4 or IPv6 address in ' +
                          nmapXmlFilename + ', skipping host', file=sys.stderr)
                    continue
                # Add host to dictionary
                if ip not in self.Hosts:
                    self.Hosts[ip] = NmapHost(ip)
                curHost = self.Hosts[ip]
                # Record what files host was found in
                if (nmapXmlFilename not in curHost.filesWithHost):
                    curHost.filesWithHost.append(nmapXmlFilename)

                # Attempt to get hostname
                try:
                    if (curHost.hostname == '' or curHost.hostname == ip):
                        # hostname will be in nmap xml if PTR (reverse lookup) record present
                        curHost.hostname = xHost.find(
                            './/hostname').get('name')
                except:
                    curHost.hostname = ip

                # Store host up status
                curHost.alive = (xHost.find('status').get('state') == 'up')

                # Parse ports
                for xPort in xHost.findall('.//port'):
                    # Only parse open ports
                    if xPort.find('.//state').get('state') == 'open':
                        curPortId = int(xPort.get('portid'))
                        curProtocol = xPort.get('protocol')
                        curService = ''
                        if (None != xPort.find('.//service')):
                            curService = xPort.find('.//service').get('name')
                        # Store port details
                        curHost.addPort(curProtocol, curPortId, curService)
                        # Store service details in global variable
                        self.addService(curService, ip, curPortId)
            # TODO: Ensure this is working correctly
            cmdLineArgsElement = nmap_xml.find('.//nmaprun')
            if cmdLineArgsElement is not None:
                cmdLineArgs = cmdLineArgsElement.get('args')
                if cmdLineArgs not in self.Arguments:
                    self.Arguments.append(cmdLineArgs)
                self.Arguments.append(cmdLineArgs)

    def addService(self, serviceName: str, ip: any, port: int) -> None:
        currentService = self.getService(serviceName)
        currentServiceHost = self.getServiceHost(currentService, ip)
        currentServiceHost.ports = set(currentServiceHost.ports)
        currentService.ports = set(currentService.ports)
        currentServiceHost.ports.add(port)
        currentService.ports.add(port)

    def getServiceHost(self, service: str, ip: any) -> None:
        for host in service.hosts:
            if host.ip == ip:
                return host
        newServiceHost = NmapHost(ip)
        service.hosts.append(newServiceHost)
        return newServiceHost

    def getService(self, serviceName: str) -> None:
        for service in self.Services:
            if service.name == serviceName:
                return service

        newService = NmapService(serviceName)
        self.Services.append(newService)
        return newService

    def getHostDictionary(self, filters=None) -> dict:
        hostDictionary = {}
        for host in self.getHosts(filters):
            hostDictionary[host.ip] = host
        return hostDictionary

    def getHosts(self, filters=None) -> list:
        '''Returns an array of hosts that match filters'''
        if filters == None:
            filters = NmapFilters()

        matchedHosts = []
        hostIps = self.helpers.sortIpList(self.Hosts)
        for ip in hostIps:
            host = copy.deepcopy(self.Hosts[ip])
            if ((not host.alive) and filters.onlyAlive) or not filters.checkHost(ip):
                continue
            matched = True
            # Check ports (if at least one filter is set)
            for protocol in constants.PROTOCOLS:
                for port in [port for port in host.ports if port.protocol == protocol]:
                    port.matched = True
                    if (
                        (filters.portFilterSet() and (filters.ports == [] or port.portId not in filters.ports)) or
                        (filters.serviceFilterSet() and (filters.services ==
                                                         [] or port.service not in filters.services))
                    ):
                        port.matched = False
                    if port.matched:
                        matched = True
            if filters.mustHavePorts and len(host.ports) == 0:
                matched = False
            # Dont check alive status as filter check has already failed
            if (matched == False and (filters.portFilterSet() or filters.serviceFilterSet() or filters.mustHavePorts)):
                continue
            if matched or (not filters.onlyAlive):
                matchedHosts.append(host)
            else:
                pass
        return matchedHosts

    def getAliveHosts(self, filters=None) -> list:
        return [host.ip for host in self.getHosts(filters) if host.alive]

    def getServices(self, filters=None) -> list:
        if filters == None:
            filters = NmapFilters()
        matchedServices = []
        for service in self.Services:
            # Check if service matches filter
            if not (
                (filters.serviceFilterSet() and (filters.services == [] or service.name not in filters.services)) or
                (filters.portFilterSet() and (filters.ports == [] or not [port for port in service.ports if port in filters.ports])) or
                (filters.hostFilterSet() and (filters.hosts == [] or not [
                 host for host in service.hosts if host in filters.hosts]))
            ):
                matchedServices.append(service)
        return matchedServices

    def getNmapCmdline(self, filters=None) -> list:
        return self.Arguments

    def generateNmapParseXml(self, filename) -> None:
        # create the file structure
        xNmapParse = ET.Element('nmapparse')
        for ip in self.Hosts:
            curHost = self.Hosts[ip]
            # Create host element
            xHost = ET.SubElement(xNmapParse, 'host')
            # Create status element
            xStatus = ET.SubElement(xHost, 'status')
            xStatus.set('state', 'up' if curHost.alive else 'down')
            # Create address element
            xAddress = ET.SubElement(xHost, 'address')
            xAddress.set('addr', curHost.ip)
            xAddress.set('addrtype', 'ipv4')
            # Create hostname element
            xHostnames = ET.SubElement(xHost, 'hostnames')
            if (curHost.hostname != ip):
                xHostname = ET.SubElement(xHostnames, 'hostname')
                xHostname.set('name', curHost.hostname)
            # Create ports element
            xPorts = ET.SubElement(xHost, 'ports')
            for port in curHost.ports:
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
            xmlData = ET.tostring(xNmapParse)
            # Format with indets
            bs = BeautifulSoup(xmlData, 'lxml-xml')
            xmlData = bs.prettify()
            # Write to file
            fhXml = open(filename, 'w')
            fhXml.write(str(xmlData))
            fhXml.close()
            self.lamePrint.sprint('Combined file saved to: ' + filename)
        except Exception as ex:
            self.lamePrint.eprint('Failed to combine files')
            self.lamePrint.eprint(str(ex))

    def getHostsByFile(self, filters=None) -> dict:
        '''Returns a dictionary with filenames as ID's and an array of hosts'''
        fileHostDict = {}
        for host in self.getHosts(filters=filters):
            for file in host.filesWithHost:
                if file not in fileHostDict:
                    fileHostDict[file] = []
                fileHostDict[file].append(host)
        return fileHostDict

    def getHostsWithinFile(self, file, filters=None) -> list:
        if (filters == None):
            filters = NmapFilters()
        return [host for host in self.getHosts(filters=filters) if file in host.filesWithHost]

    def getUniquePortIds(self, protocol=constants.PORT_OPT_COMBINED, filters=None, hosts=None) -> list:
        allPorts = set()
        if (hosts == None):
            hosts = self.getHosts(filters)
        if (filters == None):
            filters = NmapFilters()
        for host in hosts:
            if protocol == constants.PORT_OPT_TCP:
                allPorts = allPorts.union(host.getUniquePortIds(
                    constants.PORT_OPT_TCP, port_filter=filters.ports, service_filter=filters.services))
            elif protocol == constants.PORT_OPT_UDP:
                allPorts = allPorts.union(host.getUniquePortIds(
                    constants.PORT_OPT_UDP, port_filter=filters.ports, service_filter=filters.services))
            else:
                allPorts = allPorts.union(host.getUniquePortIds(
                    constants.PORT_OPT_TCP, port_filter=filters.ports, service_filter=filters.services))
                allPorts = allPorts.union(host.getUniquePortIds(
                    constants.PORT_OPT_UDP, port_filter=filters.ports, service_filter=filters.services))
        return sorted(allPorts)


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

    def getState(self) -> str:
        state = 'up'
        if not self.alive:
            state = 'down'
        return state

    def addPort(self, protocol: any, portId: any, service: any) -> None:
        self.addService(service)
        for port in self.ports:
            if port.portId == portId and port.protocol == protocol:
                # Port already exists, check if service is blank and add if possible
                if (len(port.service.strip()) == 0):
                    port.service = service
                return
        # Add port if function hasn't already exited
        self.ports.append(NmapPort(protocol, portId, service))

    def addService(self, service: any) -> None:
        if service not in self.services:
            self.services.append(service)

    def getUniquePortIds(self, protocol='', port_filter=[], service_filter=[]) -> list:
        allPortIds = []
        for port in self.ports:
            if (len(port_filter) > 0 and port.portId not in port_filter):
                continue
            if (len(service_filter) > 0 and port.service not in service_filter):
                continue
            if len(protocol) == 0 or port.protocol == protocol:
                allPortIds.append(port.portId)

        uniquePortIds = set(allPortIds)
        return sorted(uniquePortIds)

    def getHostname(self) -> str:
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
    def areFiltersSet(self) -> bool:
        return self.hostFilterSet() or self.portFilterSet() or self.serviceFilterSet() or self.onlyAlive or self.mustHavePorts

    # @property
    def hostFilterSet(self) -> bool:
        return len(self.hosts) > 0

    # @property
    def portFilterSet(self) -> bool:
        return len(self.ports) > 0

    # @property
    def serviceFilterSet(self) -> bool:
        return len(self.services) > 0

    def checkHost(self, ip: any) -> bool:
        # Always return true if no filter is set
        if not self.hostFilterSet():
            return True
        # Check if host matches any ips first
        matched = ip in [filter.filter for filter in self.hosts if filter.isIp]
        # If no match found, check if host matches any network range
        if not matched:
            for filter in [filter for filter in self.hosts if filter.isNetwork]:
                if ipaddress.ip_address(ip) in ipaddress.ip_network(filter.filter):
                    matched = True
                    break
        return matched


class NmapHostFilter:
    def __init__(self, filter, isIp):
        self.filter = filter
        self.isIp = isIp
        self.isNetwork = not isIp


class NmapHelpers:
    """
    A class that provides helper methods for working with Nmap.

    Methods:
    - printUniquePorts: Prints the unique open ports for a given set of hosts.
    - getUniquePortsOutput: Returns the unique open ports for a given set of hosts as a TextOutput object.
    - getNmapFiltersString: Returns a string representation of the Nmap filters.
    - printNmapFilters: Prints the Nmap filters.
    - getHostListOutput: Returns string representations of filtered hosts output.
    - printHosts: Prints the filtered hosts output.
    - sortIpList: Sorts a list of IP addresses in ascending order.
    - printImportSummary: Prints a summary of the imported files.
    - getServiceListOutput: Returns string representations of the service list.
    - printServiceList: Prints the service list.
    - executeCommands: Executes commands on the hosts that match the filters.
    - executeCommand: Executes a command on a specific IP address.
    - printAliveIps: Prints the list of alive IP addresses.
    - getFilesInDir: Returns a list of files in a directory that match the specified filter.
    - stringToHostFilter: Converts a string representation of a host filter to a list of filters.
    """

    def __init__(self):
        self.lamePrint = LamePrint()
        self.notify = Notify()
        self.notifyNmap = NotifyNmap()
        # self.textOutput = TextOutput()

    def printUniquePorts(self, hosts: any, option=constants.PORT_OPT_DEFAULT, filters=None) -> str:
        ...


class NmapHelpers:
    def __init__(self):
        self.lamePrint = LamePrint()
        self.notify = Notify()
        self.notifyNmap = NotifyNmap()
        self.logger = Logger()
        # self.textOutput = TextOutput()

    def printUniquePorts(self, hosts: any, option=constants.PORT_OPT_DEFAULT, filters=None) -> str:
        textOutput = self.getUniquePortsOutput(hosts, option, filters=filters)
        textOutput.printToConsole()

    def getUniquePortsOutput(self, hosts: any, option=constants.PORT_OPT_DEFAULT, filters=None):
        if filters == None:
            filters = NmapFilters()
        tcpPorts = set()
        udpPorts = set()
        allPorts = set()
        for ip in hosts:
            host = hosts[ip]
            tcpPorts = tcpPorts.union(host.getUniquePortIds(
                'tcp', port_filter=filters.ports, service_filter=filters.services))
            udpPorts = udpPorts.union(host.getUniquePortIds(
                'udp', port_filter=filters.ports, service_filter=filters.services))
        allPorts = tcpPorts.union(udpPorts)

        output = TextOutput()
        output.addHumn(self.getNmapFiltersString(filters))
        output.addHumn(self.lamePrint.getHeader(
            'Unique open port list (%s)' % (option)))
        if option == constants.PORT_OPT_DEFAULT:
            output.addHumn(self.lamePrint.getHeader('TCP:'))
            output.addMain(re.sub(r'[\[\] ]', '', str(sorted(tcpPorts))))
            output.addHumn(self.lamePrint.getHeader('UDP:'))
            output.addMain(re.sub(r'[\[\] ]', '', str(sorted(udpPorts))))
            output.addHumn(self.lamePrint.getHeader('Combined:'))
            output.addMain(re.sub(r'[\[\] ]', '', str(sorted(allPorts))))
        elif option == constants.PORT_OPT_TCP:
            output.addMain(re.sub(r'[\[\] ]', '', str(sorted(tcpPorts))))
        elif option == constants.PORT_OPT_UDP:
            output.addMain(re.sub(r'[\[\] ]', '', str(sorted(udpPorts))))
        elif option == constants.PORT_OPT_COMBINED:
            output.addMain(re.sub(r'[\[\] ]', '', str(sorted(allPorts))))
        return output

    def getNmapFiltersString(self, filters: NmapFilters) -> str:
        filterString = ""
        if filters.areFiltersSet():
            filterString += self.lamePrint.getHeader('Output filtered by:')
            if filters.hostFilterSet():
                filterString += ('Host filter [host_filter]: %s' % (
                    [filter.filter for filter in filters.hosts])) + os.linesep
            if filters.serviceFilterSet():
                filterString += ('Service filter [service_filter]: %s' %
                                 (filters.services)) + os.linesep
            if filters.portFilterSet():
                filterString += ('Port filter [port_filter]: %s' %
                                 (filters.ports)) + os.linesep
            if filters.mustHavePorts:
                filterString += ('Must have ports filter [have_ports]: %s' % str(
                    filters.mustHavePorts)) + os.linesep
            if filters.onlyAlive:
                filterString += ('Up filter [only_up]: %s' %
                                 str(filters.onlyAlive)) + os.linesep
        return filterString

    def printNmapFilters(self, filters: NmapFilters) -> None:
        filterString = self.getNmapFiltersString(filters)
        if (len(filterString) > 0):
            self.hprint(filterString)

    def getHostListOutput(self, nmapOutput: any, includePorts=True, filters=None, includeHostname=False, isTable=False) -> str:
        """Returns string representations of filtered hosts output"""
        if filters == None:
            filters = NmapFilters()

        output = TextOutput()
        output.addHumn(self.getNmapFiltersString(filters))
        output.addHumn(self.lamePrint.getHeader('Matched IP List'))

        headers = ['IP']
        if (includeHostname):
            headers.append('Hostname')
        for protocol in constants.PROTOCOLS:
            headers.append(protocol)

        tableRows = []
        # Get all hosts that are up and matched filters
        hostsOutput = []
        for host in nmapOutput.getHosts(filters=filters):
            tableRow = [host.ip]
            curHostOutput = [host.ip, '']

            if (includeHostname):
                if (host.hostname == host.ip):
                    tableRow.append('')
                else:
                    tableRow.append(host.hostname)
                    curHostOutput = [f"{host.ip} ({host.hostname})", '']

            for protocol in constants.PROTOCOLS:
                fullPortsString = ''
                for port in [port for port in host.ports if port.protocol == protocol]:
                    tmpPortString = str(port.portId)
                    if (settings.PARSER_SETTINGS.colorSupported and port.matched):
                        tmpPortString = '\033[1;32m' + \
                            tmpPortString + '\033[1;m'
                    if len(fullPortsString) > 0:
                        fullPortsString += ", "
                    fullPortsString += tmpPortString
                curHostOutput[1] += '%s:[%s]  ' % (protocol, fullPortsString)
                tableRow.append(fullPortsString)
            hostsOutput.append(curHostOutput)
            tableRows.append(tableRow)

        if (isTable):
            output.addMain(tabulate.tabulate(
                tableRows, headers=headers, tablefmt='grid', maxheadercolwidths=[None, None, None, None], maxcolwidths=[None, None, 20, 20]))
        else:
            for hostData in hostsOutput:
                if includePorts:
                    output.addMain(f'{hostData[0]}\t{hostData[1]}')
                    # output.addMain("%s\t%s" % (hostData[0], hostData[1]))
                else:
                    output.addMain(hostData[0])
        return output

    def printHosts(self, nmapOutput: any, includePorts=True, filters=None) -> None:
        textOutput = self.getHostListOutput(
            nmapOutput, includePorts=includePorts, filters=filters)
        textOutput.printToConsole()

    def sortIpList(self, ip_list: list) -> list:
        ipl = [(IP(ip).int(), ip) for ip in ip_list]
        ipl.sort()
        return [ip[1] for ip in ipl]

    def printImportSummary(self, nmapOutput: any, detailed=True) -> None:
        if (detailed):
            for file in nmapOutput.FilesImported:
                self.lamePrint.sprint('Successfully loaded ' + file)
        self.lamePrint.sprint(os.linesep + 'Successfully loaded ' +
                              str(len(nmapOutput.FilesImported)) + ' files')
        if len(nmapOutput.FilesFailedToImport) > 0:
            self.lamePrint.eprint('The following files failed to parse:')
            for file in nmapOutput.FilesFailedToImport:
                self.lamePrint.eprint('\t' + file)

    def getServiceListOutput(self, nmapOutput: any, filters=None, verbose=False, includePorts=True) -> str:
        services = nmapOutput.getServices(filters)
        output = TextOutput()
        output.addHumn(self.lamePrint.getHeader('Service List'))
        first = True
        for service in services:
            if (verbose):
                if first:
                    first = False
                else:
                    output.addMain("")
            svcString = service.name
            if (includePorts):
                svcString += ' ' + str(sorted(service.ports))
            output.addMain(svcString)
            if verbose:
                for host in service.hosts:
                    hostString = '  ' + host.ip
                    if (includePorts):
                        hostString += ' ' + str(sorted(host.ports))
                    output.addMain(hostString)
        return output

    def printServiceList(self, nmapOutput: any, filters=None, verbose=False) -> None:
        textOutput = self.getServiceListOutput(
            nmapOutput, filters=filters, verbose=verbose)
        textOutput.printToConsole()

    def executeCommands(self, cmd: any, nmapOutput: any, filters=None) -> None:
        if (filters == None):
            filters = NmapFilters()
        self.header('Running Commands')
        for host in nmapOutput.getHosts(filters):
            if len(host.ports) > 0:
                self.executeCommand(cmd, host.ip)

    def executeCommand(self, cmd: any, ip: any) -> None:
        curCommand = cmd + ' ' + ip
        self.lamePrint.hprint("Running command: '%s'" % curCommand)
        process = Popen(curCommand, shell=True, stdout=PIPE)
        output = process.stdout.read()
        self.lamePrint.hprint('Finished running command: %s' % curCommand)
        self.header("OUTPUT for '%s':" % curCommand)
        if output == '':
            print('<none>')
        else:
            print(output)
        print('')

    def printAliveIps(self, nmapOutput: any) -> None:
        self.header('Alive IP List')
        # Get all hosts that are up and matched filters
        tmpParsedHosts = nmapOutput.getAliveHosts()
        for ip in self.sortIpList(tmpParsedHosts):
            print("%s" % (ip))

    def getFilesInDir(self, directory: any, filter='', recurse=False) -> list:
        allFiles = []
        regex = re.compile(filter)
        if (recurse):
            for root, dirs, files in os.walk(directory):
                allFiles.extend([os.path.join(root, file)
                                for file in files if regex.match(os.path.join(root, file))])
        else:
            allFiles.extend([os.path.join(directory, file) for file in os.listdir(
                directory) if regex.match(os.path.join(directory, file))])
        return allFiles

    def stringToHostFilter(self, filterString: str) -> list:
        hostFilter = []
        rawHostFilterString = filterString
        # Remove any excess white space (start/end/between commas)
        # re.sub(r'[^\d\./,]', '', rawHostFilterString)
        curHostFilterString = rawHostFilterString.strip()
        # Split filter on comma, ignore empty entries and assign to filter
        tmpHostFilter = [ip.strip()
                         for ip in curHostFilterString.split(',') if len(ip) > 0]
        for curHostFilter in tmpHostFilter:
            isFilename = False
            curFilters = []
            # Check is specified filter is a file and attempt to load each line if it is
            if (os.path.isfile(curHostFilter)):
                try:
                    isFilename = True
                    fhFile = open(curHostFilter, 'r')
                    for line in fhFile:
                        if (len(line.strip()) > 0):
                            curFilters.append(line.strip())
                    fhFile.close()
                except:
                    self.lamePrint.eprint(
                        'Failed to load contents of: ' + curHostFilter)
            else:
                curFilters.append(curHostFilter)

            for filter in curFilters:
                validFilter = False
                isIp = False
                try:
                    ipaddress.ip_address(filter)
                    validFilter = True
                    isIp = True
                except ValueError:
                    pass

                try:
                    ipaddress.ip_network(filter)
                    validFilter = True
                except ValueError:
                    pass
                if (validFilter):
                    hostFilter.append(self.NmapHostFilter(filter, isIp))
                else:
                    if (isFilename):
                        self.lamePrint.eprint('Invalid host filter (within %s) option ignored: %s' % (
                            curHostFilter, filter))
                    else:
                        self.lamePrint.eprint(
                            'Invalid host filter option ignored: ' + filter)
        return hostFilter

    def getJsonValue(self, jsonData: any, id: any) -> any:
        if id in jsonData:
            return jsonData[id]
        else:
            return ''

    def getEpoch() -> int:
        return int(time.time())

    def getHostDetails(self, host: NmapHost) -> TextOutput:
        output = TextOutput()
        # Get overview
        output.addHumn(self.lamePrint.getHeader("Overview"))
        output.addMain('IP: %s' % host.ip)
        if (host.ip != host.hostname):
            output.addMain('Hostname: %s' % host.hostname)
        output.addMain("State: %s" % host.getState())
        openTcp = len(host.getUniquePortIds(constants.PORT_OPT_TCP))
        openUdp = len(host.getUniquePortIds(constants.PORT_OPT_UDP))
        output.addMain('TCP ports open: %s' % openTcp)
        output.addMain('UDP ports open: %s' % openUdp)
        output.addMain('Total ports open: %s' % (openTcp + openUdp))

        # Output port details
        output.addHumn(self.lamePrint.getHeader('Ports / Services'))
        portTableHeaders = ['Port', 'Protocol', 'Service']
        output.addMain(tabulate.tabulate([[port.portId, port.protocol, port.service]
                                          for port in host.ports], headers=portTableHeaders, tablefmt='github'))

        # Output files found in
        output.addHumn(self.lamePrint.getHeader('Files Containing Host'))
        if (len(host.filesWithHost) == 0):
            output.addErrr('Host not present within any files')
        else:
            for file in host.filesWithHost:
                output.addMain(file)

        return output

    def wrap_text(self, text: any, max_chars=50) -> str:
        return os.linesep.join(textwrap.wrap(text, max_chars))

    def getNmapFiles(self, fileOrDir: any, recurse=False) -> list:
        if not os.path.exists(fileOrDir):
            raise FileNotFoundError(
                f"No such file or directory: '{fileOrDir}'")
        if os.path.isdir(fileOrDir):
            return self.getFilesInDir(fileOrDir, filter=r'.*\.xml$', recurse=recurse)
        else:
            return [fileOrDir]
