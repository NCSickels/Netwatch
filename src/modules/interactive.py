import random
import textwrap
import os
import argparse
import re
import cmd2
import tabulate
from rich.console import Console
from typing import List

from modules.nmap import NmapFilters, NmapHostFilter, NmapHelpers
from modules import constants
from config import settings as settings
from modules.termutils import ColorConfig, LamePrint, Color, TextOutput, TextOutputEntry
from logger import *


class TerminalBase(cmd2.Cmd):
    def print_text_output(self, text_output):
        for line in text_output.entries:
            if (line.output == constants.TEXT_NORMAL):
                self.poutput(line.get_text())
            elif (line.output == constants.TEXT_ERROR):
                self.perror(line.get_text())
            # elif (not self.quiet) and (not self.redirecting) and settings.print_human_friendly_text:
            elif (not self.quiet) and settings.PARSER_SETTINGS.print_human_friendly_text:
                if (line.output == constants.TEXT_FRIENDLY):
                    self.pfeedback(line.get_text())
                elif (line.output == constants.TEXT_SUCCESS):
                    self.pfeedback(line.get_text())
                else:
                    self.poutput(line.get_text())


class NmapTerminal(TerminalBase):
    """
    A class representing an interactive terminal for Nmap commands.

    Attributes:
    - CMD_CAT_NMAP: A constant representing the category for Nmap commands.
    - CMD_CAT_FILTER: A constant representing the category for configuring filters.
    - service_filter: A string representing the service filter.
    - port_filter: A string representing the port filter.
    - host_filter: A string representing the host filter.
    - include_ports: A boolean indicating whether to include ports in the output.
    - include_hostname: A boolean indicating whether to include hostnames in the output.
    - have_ports: A boolean indicating whether hosts with no open ports should be excluded from the output.
    - only_up: A boolean indicating whether hosts that are down should be excluded from the output.
    - verbose: A boolean indicating whether to show verbose service information.
    - raw: A boolean indicating whether to show raw output without headings.
    - settable: A list of settable options.
    - prompt: A string representing the prompt for the terminal.
    - intro: A string representing the introduction message for the terminal.

    Methods:
    - __init__: Initializes the NmapTerminal object.
    - complete_unset: Completes the unset command by providing suggestions for unsettable options.
    - complete_set: Completes the set command by providing suggestions for settable options.
    - match_service: Tries to match a service based on the given text and prefix.
    - ip_completer: Completes the IP address argument for the host command.
    - complete_file: Completes the file argument for the file command.
    - complete_ports: Completes the option argument for the ports command.
    - complete_import: Completes the import command by providing suggestions for file paths.
    - do_exit: Exits the interactive prompt.
    - do_unset_all: Resets all user options to default values.
    - do_unset: Unsets the specified user option.
    - do_host: Prints details for the specified host.
    - do_list: Lists all IP addresses matching the filter.
    - do_tlist: Lists all IP addresses matching the filter as a table.
    - do_file: Prints details for the specified file.
    - do_services: Lists all services with optional verbose output.
    - do_ports: Lists unique ports with optional filtering.
    """


class NmapTerminal(TerminalBase):
    # region Setup defaults

    service_filter = ''
    port_filter = ''
    host_filter = ''
    include_ports = True
    include_hostname = True
    have_ports = True
    only_up = True
    verbose = True
    raw = False

    settable = [constants.OPT_INCLUDE_PORTS, constants.OPT_INCLUDE_HOSTNAME, constants.OPT_SERVICE_FILTER, constants.OPT_PORT_FILTER,
                constants.OPT_HOST_FILTER, constants.OPT_UP, constants.OPT_HAVE_PORTS, constants.OPT_VERBOSE, constants.OPT_RAW]

#     intro = """\nWelcome to nmap parse! Type ? to list commands
#   \033[1;30mTip: You can send output to clipboard using the redirect '>' operator without a filename\033[1;m
#   \033[1;30mTip: Set quiet to true to only get raw command output (no headings)\033[1;m"""

    # endregion

    def __init__(self, nmap_output, *args, **kwargs):
        super().__init__(*args, **kwargs, allow_cli_args=False)
        self.print_random_banner()
        self.nmap_output = nmap_output
        self.helpers = NmapHelpers()
        self.color_config = ColorConfig()
        self.lame_print = LamePrint()
        self.color = Color()
        self.prompt = '\n\033[4m\033[1;30mnmap-parse\033[1;30m\033[0m\033[1;30m ~#\033[0;m '

        cmd2.utils.categorize(self.do_set, constants.CMD_CAT_FILTER)

        self.add_settable(cmd2.Settable(constants.OPT_INCLUDE_PORTS, bool,
                          "Toggles whether ports are included in 'list/services' output  [ True / False ]", self))
        self.add_settable(cmd2.Settable(constants.OPT_INCLUDE_HOSTNAME, bool,
                          "Toggles whether hostnames are included in 'list' output  [ True / False ]", self))
        self.add_settable(cmd2.Settable(constants.OPT_SERVICE_FILTER, str,
                          "Comma seperated list of services to show, e.g. \"http,ntp\"", self))
        self.add_settable(cmd2.Settable(constants.OPT_PORT_FILTER, str,
                          "Comma seperated list of ports to show, e.g. \"80,123\"", self))
        self.add_settable(cmd2.Settable(constants.OPT_HOST_FILTER, str,
                          "Comma seperated list of hosts to show, e.g. \"127.0.0.1,127.0.0.2\"", self))
        self.add_settable(cmd2.Settable(constants.OPT_UP, bool,
                          "When enabled, any hosts which were down will be excluded from output  [ True / False ]", self))
        self.add_settable(cmd2.Settable(constants.OPT_HAVE_PORTS, bool,
                          "When enabled, hosts with no open ports are excluded from output  [ True / False ]", self))
        self.add_settable(cmd2.Settable(constants.OPT_VERBOSE, bool,
                          "Shows verbose service information  [ True / False ]", self))
        self.add_settable(cmd2.Settable(constants.OPT_RAW, bool,
                          "Shows raw output (no headings)  [ True / False ]", self))

    # region Completion Methods
    def complete_unset(self, text: any, line: any, begidx: any, endidx: any) -> List[str]:
        # remove 'unset' from first array slot
        split_text = line.split()[1:]
        if (line.strip() == 'unset'):
            return [option for option in self.settable]
        if (len(split_text) == 1):
            return [option for option in self.settable if option.startswith(split_text[0].lower()) and not (option == split_text[0].lower())]

    def complete_set(self, text: any, line: any, begidx: any, endidx: any) -> List[str]:
        # remove 'set' from first array slot
        tmp_split = line.split()[1:]
        # Remove any additional flags (e.g. -v)
        split_text = [i for i in tmp_split if not i.startswith("-")]
        if (line.strip() == 'set'):
            return [option for option in self.settable]
        if (len(split_text) == 1):
            return [option for option in self.settable if option.startswith(split_text[0].lower()) and not (option == split_text[0].lower())]
        if (len(split_text) == 2):
            if split_text[0] == constants.OPT_SERVICE_FILTER:
                # need to split this value on comma incase user specified more than one service
                # then use last split. Also remove quotes
                tmp_text = split_text[1].replace("\"", "")
                tmp_services = tmp_text.split(',')
                cur_service = tmp_services[-1:][0]
                prefix = ''
                if len(tmp_services) > 1:
                    prefix = ','.join(tmp_services[:-1]) + ','
                return self.match_service(cur_service, prefix)
            elif split_text[0] == constants.OPT_HOST_FILTER:
                # need to split this value on comma incase user specified more than one IP
                # then use last split. Also remove quotes
                tmp_text = split_text[1].replace("\"", "")
                tmp_hosts = tmp_text.split(',')
                cur_host = tmp_hosts[-1:][0]
                prefix = ''
                if len(tmp_hosts) > 1:
                    prefix = ','.join(tmp_hosts[:-1]) + ','
                return [(prefix + ip) for ip in self.nmap_output.Hosts if cur_host in ip]
        return [text]

    def match_service(self, text: any, prefix: any) -> List[str]:
        matches = []
        try:
            service_files = ['/usr/share/nmap/nmap-services', '/etc/services',
                             'C:\\windows\\system32\\drivers\\etc\\services']
            for service_file in service_files:
                if (os.path.isfile(service_file)):
                    fhservices = open(service_file, 'r')
                    tmp_regex = '(' + text + r'\S*)\s+\d+/(?:tcp|udp)'
                    reg = re.compile(tmp_regex)
                    for line in fhservices:
                        matches += [match for match in reg.findall(
                            line) if match not in matches]
                    fhservices.close()
                    break
        except:
            raise
        return [(prefix + match) for match in matches]

    # text - Current text typed for current parameter user is typing
    # line - Full command entered so far
    # begidx and endidx are indices of start and end of current parameter
    # arg_tokens = dictionary of tokens
    def ip_completer(self, text: any, line: any, begidx: any, endidx: any, arg_tokens: any) -> List[str]:
        sText = text.strip()
        ips = [x for x in self.nmap_output.Hosts.keys() if x.startswith(sText)]
        return ips

    def complete_file(self, text: any, line: any, begidx: any, endidx: any) -> List[str]:
        return [file for file in self.nmap_output.FilesImported if file.startswith(text)]

    def complete_ports(self, text: any, line: any, begidx: any, endidx: any) -> List[str]:
        return self.basic_complete(text, line, begidx, endidx, constants.PORT_OPTIONS)

    complete_import = cmd2.Cmd.path_complete
    # endregion

    # region Terminal Commands
    @cmd2.with_category(constants.CMD_CAT_CORE)
    def do_exit(self, inp: str) -> bool:
        '''Exit the interactive prompt'''
        print("\nBye.\n")
        return True

    @cmd2.with_category(constants.CMD_CAT_CORE)
    def do_clear(self, inp: str) -> None:
        '''Clear the screen'''
        os.system('clear')

    @cmd2.with_category(constants.CMD_CAT_FILTER)
    def do_unset_all(self, inp: str) -> None:
        '''"unset_all" will reset all user options to default values'''
        console_output = TextOutput()
        for option in self.settable:
            if (self.unset_option(option)):
                console_output.add_humn("Unset [" + option + "]")
            else:
                console_output.add_error("Failed to unset [%s]" % option)
        self.print_text_output(console_output)

    @cmd2.with_category(constants.CMD_CAT_FILTER)
    def do_unset(self, inp: str) -> None:
        '''"unset [option]" will unset the specified user option'''
        split_text = inp.split()
        if (len(split_text) != 1):
            print("Invalid use of unset command")
        else:
            success = self.unset_option(split_text[0].lower())
            if (success):
                print("Unset [" + split_text[0].lower() + "] ==> ''")

    host_parser = cmd2.Cmd2ArgumentParser()
    host_parser.add_argument(
        'ip', help="Show details of specified host", type=str, completer=ip_completer)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    @cmd2.with_argparser(host_parser)
    def do_host(self, args: any) -> None:
        '''Print details for specified host
        Useage: "host [ip address]'''
        ip = args.ip.strip()
        if (ip not in self.nmap_output.Hosts):
            self.perror("Host not found: " + ip)
            return
        cur_host = self.nmap_output.Hosts[ip]
        self.print_text_output(self.helpers.get_host_details(cur_host))

    banner_parser = cmd2.Cmd2ArgumentParser()
    banner_parser.add_argument(
        'service', help="Show banner for specified service", type=str, completer=match_service)

    # BUG: This command is not working
    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_banner(self, inp: str) -> None:
        '''Print banner for specified service'''
        service = inp.strip()
        if (service not in self.nmap_output.Services):
            self.perror("Service not found: " + service)
            return
        cur_service = self.nmap_output.Services[service]
        # TODO: Check this
        self.print_text_output(self.helpers.getServiceBanner(cur_service))

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_list(self, inp: str) -> None:
        '''List all IP's matching filter'''
        console_output = self.helpers.get_host_list_output(self.nmap_output, include_ports=self.include_ports, filters=self.get_filters(
        ), include_hostname=self.include_hostname, is_table=False)
        self.print_text_output(console_output)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_tlist(self, inp: str) -> None:
        '''List all IP's matching filter as table'''
        console_output = self.helpers.get_host_list_output(self.nmap_output, include_ports=self.include_ports, filters=self.get_filters(
        ), include_hostname=self.include_hostname, is_table=True)
        self.print_text_output(console_output)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_file(self, inp: str) -> None:
        '''Print details for specified file'''
        file = inp.strip().replace("\"", "")
        if (file not in self.nmap_output.FilesImported):
            self.perror("File not found: " + file)
            return

        filters = self.get_filters()
        self.pfeedback(self.helpers.get_filters_string(filters))
        hosts = self.nmap_output.get_hosts_within_file(file, filters=filters)

        self.pfeedback(self.lame_print.get_header("Hosts within file"))
        if self.verbose:
            headers = ['IP', 'Hostname', 'State',
                       'TCP Ports (count)', 'UDP Ports (count)']
            verbose_output = []
            for host in hosts:
                verbose_output.append([host.ip, host.get_hostname(), host.get_state(),
                                      len(host.get_unique_port_ids(
                                          constants.PORT_OPT_TCP)),
                                      len(host.get_unique_port_ids(constants.PORT_OPT_UDP))])
            self.poutput(tabulate.tabulate(
                verbose_output, headers=headers, tablefmt="github"))
        else:
            for host in hosts:
                self.poutput(host.ip)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_services(self, inp: str) -> None:
        '''Lists all services (supports verbose output)'''
        console_output = self.helpers.get_service_list_output(self.nmap_output, filters=self.get_filters(
        ), verbose=self.verbose, include_ports=self.include_ports)
        self.print_text_output(console_output)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_ports(self, inp: str) -> None:
        '''Lists unique ports. Usage "ports [default/tcp/udp/combined]"'''
        option = constants.PORT_OPT_DEFAULT
        userOp = inp.strip().lower()
        if (userOp in constants.PORT_OPTIONS):
            option = userOp
        filters = self.get_filters()
        console_output = self.helpers.get_unique_ports_output(
            self.nmap_output.get_host_dict(filters), option, filters=filters)
        self.print_text_output(console_output)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    @cmd2.with_argument_list
    def do_import(self, args: List[str]) -> None:
        '''Import additional nmap files or directories

        Usage: import [filename/directory]
        '''
        if not args:
            self.perror(
                'import requires a path to a file/directory as an argument')
            return
        all_files = []
        for file in args:
            all_files.extend(self.helpers.get_nmap_files(file, recurse=True))
        self.nmap_output.parse_nmap_xml(all_files)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_import_summary(self, inp: str) -> None:
        '''Displays list of imported files'''

        self.pfeedback(self.lame_print.get_header(
            "Successfully Imported Files"))
        if (len(self.nmap_output.FilesImported) > 0):
            if self.verbose:
                headers = ['Filename', 'Hosts Scanned', 'Alive Hosts']
                verbose_output = []
                files_without_hosts = []
                filters = NmapFilters(defaultBool=False)
                hosts_by_file = self.nmap_output.get_hosts_by_file(filters)
                for file in self.nmap_output.FilesImported:
                    if file in hosts_by_file:
                        scanned_hosts = hosts_by_file[file]
                        alive_host_count = len(
                            [host for host in scanned_hosts if host.alive])
                        verbose_output.append(
                            [file, len(scanned_hosts), alive_host_count])
                    else:
                        verbose_output.append([file, 0, 0])
                        files_without_hosts.append(file)
                self.poutput(tabulate.tabulate(
                    verbose_output, headers=headers))
                if (len(files_without_hosts) > 0):
                    self.perror("\nThe following file(s) had no hosts:")
                    for file in files_without_hosts:
                        self.perror("  - " + file)
            else:
                for file in self.nmap_output.FilesImported:
                    self.poutput(file)
        else:
            self.perror("No files were imported successfully.")
        print()

        if (len(self.nmap_output.FilesFailedToImport) > 0):
            self.pfeedback(self.lame_print.get_header("Failed Imports"))
            for file in self.nmap_output.FilesFailedToImport:
                self.perror(file)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_scanned_hosts(self, inp: str) -> None:
        '''List all hosts scanned'''
        self.pfeedback(self.lame_print.get_header('Scanned Hosts'))

        filters = self.get_filters()
        filters.onlyAlive = False

        for line in [host.ip for host in self.nmap_output.get_hosts(filters=filters)]:
            self.poutput(line)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_all_hosts(self, inp: str) -> None:
        '''Print details for all hosts'''
        self.do_alive_hosts(inp)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_alive_hosts(self, inp: str) -> None:
        '''List alive hosts'''
        self.pfeedback(self.lame_print.get_header('Alive Hosts'))
        for ip in self.nmap_output.get_alive_hosts(self.get_filters()):
            self.poutput(ip)

    @cmd2.with_category(constants.CMD_CAT_NMAP)
    def do_nmap_cmdline(self, inp: str) -> None:
        '''Prints the nmap command line arguments used to generate the scan output'''
        self.poutput(self.nmap_output.get_nmap_cmdline())
    # endregion

    # region Helper Methods
    def unset_option(self, option: any) -> bool:
        match(option):
            case constants.OPT_HAVE_PORTS:
                self.have_ports = True
            case constants.OPT_HOST_FILTER:
                self.host_filter = ''
            case constants.OPT_PORT_FILTER:
                self.port_filter = ''
            case constants.OPT_RAW:
                self.raw = False
            case constants.OPT_SERVICE_FILTER:
                self.service_filter = ''
            case constants.OPT_VERBOSE:
                self.verbose = True
            case constants.OPT_INCLUDE_PORTS:
                self.include_ports = True
            case constants.OPT_UP:
                self.only_up = True
            case constants.OPT_INCLUDE_HOSTNAME:
                self.include_hostname = True
            case _:
                return False
        return True

    def get_port_filter(self) -> List[int]:
        port_filter = []
        raw_port_filter_string = self.port_filter
        # Check only contains valid chars
        if (re.match(r'^([\d\s,]+)$', raw_port_filter_string)):
            # Remove any excess white space (start/end/between commas)
            cur_port_filter_string = re.sub(
                r'[^\d,]', '', raw_port_filter_string)
            # Split filter on comma, ignore empty entries and assign to filter
            port_filter = [int(port) for port in cur_port_filter_string.split(
                ',') if len(port) > 0]
        return port_filter

    def get_host_filter(self) -> NmapHostFilter:
        return self.helpers.string_to_host_filter(self.host_filter)

    def get_service_filter(self) -> List[str]:
        return [option for option in self.service_filter.split(',') if len(option.strip()) > 0]

    def get_filters(self) -> NmapFilters:
        filters = NmapFilters()
        filters.services = self.get_service_filter()
        filters.ports = self.get_port_filter()
        # TODO: Check this
        filters.hosts = self.get_host_filter()
        filters.onlyAlive = self.only_up
        filters.mustHavePorts = self.have_ports
        return filters

    def print_random_banner(self) -> None:
        banners = ["""
          ███╗   ██╗███╗   ███╗ █████╗ ██████╗
          ████╗  ██║████╗ ████║██╔══██╗██╔══██╗
          ██╔██╗ ██║██╔████╔██║███████║██████╔╝
          ██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝
          ██║ ╚████║██║ ╚═╝ ██║██║  ██║██║
          ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
        ██████╗  █████╗ ██████╗ ███████╗███████╗
        ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝
        ██████╔╝███████║██████╔╝███████╗█████╗
        ██╔═══╝ ██╔══██║██╔══██╗╚════██║██╔══╝
        ██║     ██║  ██║██║  ██║███████║███████╗
        ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
                        """, """
             /$$   /$$ /$$      /$$  /$$$$$$  /$$$$$$$
            | $$$ | $$| $$$    /$$$ /$$__  $$| $$__  $$
            | $$$$| $$| $$$$  /$$$$| $$  \ $$| $$  \ $$
            | $$ $$ $$| $$ $$/$$ $$| $$$$$$$$| $$$$$$$/
            | $$  $$$$| $$  $$$| $$| $$__  $$| $$____/
            | $$\  $$$| $$\  $ | $$| $$  | $$| $$
            | $$ \  $$| $$ \/  | $$| $$  | $$| $$
            |__/  \__/|__/     |__/|__/  |__/|__/
         /$$$$$$$   /$$$$$$  /$$$$$$$   /$$$$$$  /$$$$$$$$
        | $$__  $$ /$$__  $$| $$__  $$ /$$__  $$| $$_____/
        | $$  \ $$| $$  \ $$| $$  \ $$| $$  \__/| $$
        | $$$$$$$/| $$$$$$$$| $$$$$$$/|  $$$$$$ | $$$$$
        | $$____/ | $$__  $$| $$__  $$ \____  $$| $$__/
        | $$      | $$  | $$| $$  \ $$ /$$  \ $$| $$
        | $$      | $$  | $$| $$  | $$|  $$$$$$/| $$$$$$$$
        |__/      |__/  |__/|__/  |__/ \______/ |________/
                        """]
        cur_banner = textwrap.dedent(random.choice(banners)).replace(
            os.linesep, os.linesep + "  ")
        max_len = 0
        for line in cur_banner.split('\n'):
            if len(line) > max_len:
                max_len = len(line)
        cur_banner = ("-" * max_len) + \
            f"\n[{Color.AC1}]" + cur_banner + \
            f"[bright_white] \n" + ("-" * max_len)
        # "\n\033[1;34m" + cur_banner + "\033[0;m \n" + ("-" * max_len)
        Console().print(cur_banner)
        # self.poutput(cur_banner)

    # endregion
