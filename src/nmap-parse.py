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
from config import parsersettings as settings
from modules.nmap import NmapOutput, NmapFilters, NmapHelpers
from modules.termutils import ColorConfig, LamePrint, Color
from modules.notify import *
VERSION = "3.0.0"
RELEASE_DATE = "2023-11-28"


class ParserProgram:
    def __init__(self):
        self.helpers = NmapHelpers()
        self.colorConfig = ColorConfig()
        self.lamePrint = LamePrint()

    def run(self):
        parser = argparse.ArgumentParser(
            usage="{prog} [options]... <nmap-xml-files> <command> [command-parameters]...")
        parser.add_argument(
            "xml_files", nargs="+", help="Nmap XML files or directories containing XML files")
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
        # Now you can access the arguments using args.ports, args.svcFilter, etc.

        if (args.version):
            print("Netwatch Nmap Data Parser Version %s\nReleased: %s" %
                  (VERSION, RELEASE_DATE))
            return

        # Determine whether to output headings
        settings.printHumanFriendlyText = not args.raw
        settings.colorSupported = self.colorConfig.supportsColor()

        # Find all XML files
        nmapXmlFilenames = []
        for arg in args.xml_files:
            nmapXmlFilenames.extend(
                self.helpers.getNmapFiles(arg, recurse=args.recurse))

        # Exit if no XML files found
        if nmapXmlFilenames == []:
            print('No Nmap XML files found.\n')
            parser.print_help()
            sys.exit(1)

        portFilter = []
        serviceFilter = []
        filters = NmapFilters()
        if not args.interactive:
            # Check if only specific ports should be parsed
            if args.ports:
                portFilter = list(map(int, args.ports.split(',')))
                filters.ports = portFilter
                self.lamePrint.hprint('Set port filter to %s' % portFilter)

            # Check if only specific ports should be parsed
            if args.svcFilter:
                serviceFilter = args.svcFilter.split(',')
                filters.services = serviceFilter
                self.lamePrint.hprint(
                    'Set service filter to %s' % serviceFilter)

        # Parse nmap files
        nmapOutput = NmapOutput(nmapXmlFilenames)
        # Output successfully loaded and any failed files
        self.helpers.printImportSummary(nmapOutput, False)

        # Print import summary if requested
        if args.importedFiles:
            self.lamePrint.header("Import Summary")
            self.helpers.printImportSummary(nmapOutput, True)

        # Check if default flags were used
        defaultFlags = not args.ipList and not args.aliveHosts and not args.servicelist and not args.verbose and not args.cmd and not args.combine and not args.uniquePorts and not args.importedFiles

        if args.combine:
            nmapOutput.generateNmapParseXml(args.combine)

        if not args.interactive:
            if (defaultFlags):
                defaultFilters = NmapFilters()
                defaultFilters.onlyAlive = False
                defaultFilters.mustHavePorts = False
                self.helpers.printHosts(nmapOutput, filters=defaultFilters)
                self.helpers.printUniquePorts(
                    nmapOutput.getHostDictionary(), filters=defaultFilters)

            if args.ipList:
                self.helpers.printHosts(nmapOutput, filters=filters)

            if (args.uniquePorts):
                self.helpers.printUniquePorts(nmapOutput.getHostDictionary(
                    filters=filters), filters=filters)

            if args.aliveHosts:
                self.helpers.printAliveIps(nmapOutput)

            if args.servicelist or args.verbose:
                self.helpers.printServiceList(
                    nmapOutput, filters=filters, verbose=args.verbose)

            if args.cmd:
                self.helpers.executeCommands(
                    args.cmd, nmapOutput, filters=filters)

            if settings.printHumanFriendlyText and (defaultFlags or args.hostSummary):
                self.lamePrint.hprint("\nSummary\n-------")
                self.lamePrint.hprint("Total hosts: %s" %
                                      str(len(nmapOutput.Hosts)))
                self.lamePrint.hprint("Alive hosts: %s" %
                                      str(len(nmapOutput.getAliveHosts(filters))))
        else:
            enterInteractiveShell(nmapOutput)


def enterInteractiveShell(nmapOutput):
    prompt = interactive.NmapTerminal(nmapOutput)
    sys.exit(prompt.cmdloop())


def main():
    parserProgram = ParserProgram()
    parserProgram.run()


if __name__ == "__main__":
    main()
