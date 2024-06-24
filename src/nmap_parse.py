#!/usr/bin/python3
#
#
#         ███╗   ██╗███╗   ███╗ █████╗ ██████╗
#         ████╗  ██║████╗ ████║██╔══██╗██╔══██╗
#         ██╔██╗ ██║██╔████╔██║███████║██████╔╝
#         ██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝
#         ██║ ╚████║██║ ╚═╝ ██║██║  ██║██║
#         ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝
#       ██████╗  █████╗ ██████╗ ███████╗███████╗
#       ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝
#       ██████╔╝███████║██████╔╝███████╗█████╗
#       ██╔═══╝ ██╔══██║██╔══██╗╚════██║██╔══╝
#       ██║     ██║  ██║██║  ██║███████║███████╗
#       ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝
#
#   Netwatch v3.0.0
#   by: @NCSickels
#
import sys
import argparse
from modules import interactive
from config import settings as settings
from modules import *

VERSION = "3.0.0"
RELEASE_DATE = "2023-11-28"


class ParserProgram:
    def __init__(self):
        self.helpers = NmapHelpers()
        self.color_config = ColorConfig()
        self.lame_print = LamePrint()

    def run(self):
        parser = argparse.ArgumentParser(
            usage="{prog} [options]... <nmap-xml-files> <command> [command-parameters]...")
        parser.add_argument(
            "xml_files", nargs="*", help="Nmap XML files or directories containing XML files")
        # TODO: Fix this -> Port filter not correctly parsed
        parser.add_argument("-p", "--port", dest="ports",
                            help="Optional port filter argument e.g. 80 or 80,443", metavar="PORTS")
        parser.add_argument("--service", dest="svcFilter",
                            help="Optional service filter argument e.g. http or ntp,http (only used in conjunction with -s)")
        parser.add_argument("-e", "--exec", dest="cmd",
                            help="Script or tool to run on each IP remaining after port filter is applied. IP will be appended to end of script command line", metavar="CMD")
        parser.add_argument("-l", "--iplist", dest="ipList",
                            action="store_true", help="Print plain list of matching IPs")
        parser.add_argument("-a", "--alive-hosts", dest="aliveHosts",
                            action="store_true", help="Print plain list of all alive IPs")
        parser.add_argument("-s", "--service-list", dest="servicelist",
                            action="store_true", help="Also print list of unique services with names")
        parser.add_argument("-S", "--host-summary", dest="hostSummary",
                            action="store_true", help="Show summary of scanned/alive hosts (default)")
        parser.add_argument("-v", "--verbose", dest="verbose",
                            action="store_true", help="Verbose service list")
        parser.add_argument("-u", "--unique-ports", dest="uniquePorts",
                            action="store_true", default=False, help="Print list of unique open ports")
        parser.add_argument("-R", "--raw", dest="raw", action="store_true",
                            help="Only print raw output (no headers)")
        parser.add_argument("-r", "--recurse", dest="recurse", action="store_true",
                            help="Recurse subdirectories if directory provided for nmap files")
        parser.add_argument("-i", "--interactive", dest="interactive",
                            action="store_true", help="Enter interactive shell")
        parser.add_argument("-c", "--combine", dest="combine",
                            help="Combine all input files into single nmap-parse compatible xml file")
        parser.add_argument("--imported-files", dest="importedFiles",
                            action="store_true", help="List successfully imported files")
        parser.add_argument("-V", "--version", dest="version",
                            action="store_true", help="Print version info")
        # (options, args) = parser.parse_args()
        args = parser.parse_args()
        # Access arguments using args.port, args.service, etc.

        if (args.version):
            print(f'Netwatch Nmap Data Parser Version ' +
                  f'{VERSION}\nReleased: {RELEASE_DATE}')
            return

        # Determine whether to output headings
        settings.PARSER_SETTINGS.print_human_friendly_text = not args.raw
        settings.PARSER_SETTINGS.color_supported = self.color_config.color_support()

        # Find all XML files
        xml_filenames = []
        for arg in args.xml_files:
            xml_filenames.extend(
                self.helpers.get_nmap_files(arg, recurse=args.recurse))

        # Exit if no XML files found
        if xml_filenames == []:
            print('No Nmap XML files found.\n')
            parser.print_help()
            sys.exit(1)

        port_filter = []
        service_filter = []
        filters = NmapFilters()
        if not args.interactive:
            # Check if only specific ports should be parsed
            if args.ports:
                port_filter = list(map(int, args.ports.split(',')))
                filters.ports = port_filter
                self.lame_print.hprint(f'Set port filter to {port_filter}')

            # Check if only specific ports should be parsed
            if args.svcFilter:
                service_filter = args.svcFilter.split(',')
                filters.services = service_filter
                self.lame_print.hprint(
                    f'Set service filter to {service_filter}')

        # Parse nmap files
        nmap_output = NmapOutput(xml_filenames)
        # Output successfully loaded and any failed files
        self.helpers.print_import_summary(nmap_output, False)

        # Print import summary if requested
        if args.importedFiles:
            self.lame_print.header('Import Summary')
            self.helpers.print_import_summary(nmap_output, True)

        # Check if default flags were used
        defaultFlags = not args.ipList and not args.aliveHosts and not args.servicelist and not args.verbose and not args.cmd and not args.combine and not args.uniquePorts and not args.importedFiles

        if args.combine:
            nmap_output.generate_nmap_parse_xml(args.combine)

        if not args.interactive:
            if (defaultFlags):
                defaultFilters = NmapFilters()
                defaultFilters.onlyAlive = False
                defaultFilters.mustHavePorts = False
                self.helpers.print_hosts(nmap_output, filters=defaultFilters)
                self.helpers.print_unique_ports(
                    nmap_output.get_host_dict(), filters=defaultFilters)

            if args.ipList:
                self.helpers.print_hosts(nmap_output, filters=filters)

            if (args.uniquePorts):
                self.helpers.print_unique_ports(nmap_output.get_host_dict(
                    filters=filters), filters=filters)

            if args.aliveHosts:
                self.helpers.print_alive_ips(nmap_output)

            if args.servicelist or args.verbose:
                self.helpers.print_service_list(
                    nmap_output, filters=filters, verbose=args.verbose)

            if args.cmd:
                self.helpers.execute_commands(
                    args.cmd, nmap_output, filters=filters)

            if settings.PARSER_SETTINGS.print_human_friendly_text and (defaultFlags or args.hostSummary):
                self.lame_print.hprint('\nSummary\n-------')
                self.lame_print.hprint(
                    f'Total hosts: {str(len(nmap_output.Hosts))}')
                self.lame_print.hprint(
                    f'Alive hosts: {str(len(nmap_output.get_alive_hosts(filters)))}')
        else:
            enterInteractiveShell(nmap_output)


def enterInteractiveShell(nmap_output):
    prompt = interactive.NmapTerminal(nmap_output)
    sys.exit(prompt.cmdloop())


def main():
    parser_program = ParserProgram()
    parser_program.run()


if __name__ == "__main__":
    main()
