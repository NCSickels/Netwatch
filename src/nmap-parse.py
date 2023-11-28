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
from optparse import OptionParser
from modules import interactive
from config import parsersettings as settings
from modules.nmap import NmapOutput, NmapService, NmapHost, NmapPort, NmapFilters, NmapHostFilter, NmapHelpers
from modules.termutils import ColorConfig, LamePrint, Color, Notify, NotifyNmap
VERSION = "3.0.0"
RELEASE_DATE = "2023-11-28"


class ParserProgram:
    def __init__(self):
        self.helpers = NmapHelpers()
        self.colorConfig = ColorConfig()
        self.lamePrint = LamePrint()

    def run(self):
        parser = OptionParser(
            usage="%prog [options] [list of nmap xml files or directories containing xml files]")
        parser.add_option("-p", "--port", dest="ports",
                          help="Optional port filter argument e.g. 80 or 80,443", metavar="PORTS")
        parser.add_option("--service", dest="svcFilter",
                          help="Optional service filter argument e.g. http or ntp,http (only used in conjunction with -s)")
        parser.add_option("-e", "--exec", dest="cmd",
                          help="Script or tool to run on each IP remaining after port filter is applied. IP will be appended to end of script command line", metavar="CMD")
        parser.add_option("-l", "--iplist", dest="ipList",
                          action="store_true", help="Print plain list of matching IPs")
        parser.add_option("-a", "--alive-hosts", dest="aliveHosts",
                          action="store_true", help="Print plain list of all alive IPs")
        parser.add_option("-s", "--service-list", dest="servicelist",
                          action="store_true", help="Also print list of unique services with names")
        parser.add_option("-S", "--host-summary", dest="hostSummary",
                          action="store_true", help="Show summary of scanned/alive hosts (default)")
        parser.add_option("-v", "--verbose", dest="verbose",
                          action="store_true", help="Verbose service list")
        parser.add_option("-u", "--unique-ports", dest="uniquePorts",
                          action="store_true", default=False, help="Print list of unique open ports")
        parser.add_option("-R", "--raw", dest="raw", action="store_true",
                          help="Only print raw output (no headers)")
        parser.add_option("-r", "--recurse", dest="recurse", action="store_true",
                          help="Recurse subdirectories if directory provided for nmap files")
        parser.add_option("-i", "--interactive", dest="interactive",
                          action="store_true", help="Enter interactive shell")
        parser.add_option("-c", "--combine", dest="combine",
                          help="Combine all input files into single nmap-parse compatible xml file")
        parser.add_option("--imported-files", dest="importedFiles",
                          action="store_true", help="List successfully imported files")
        parser.add_option("-V", "--version", dest="version",
                          action="store_true", help="Print version info")
        (options, args) = parser.parse_args()

        if (options.version):
            print("Netwatch Nmap Data Parser Version %s\nReleased: %s" %
                  (VERSION, RELEASE_DATE))
            return

        # Determine whether to output headings
        settings.printHumanFriendlyText = not options.raw
        settings.colorSupported = self.colorConfig.supportsColor()

        # Find all XML files
        nmapXmlFilenames = []
        for arg in args:
            nmapXmlFilenames.extend(
                self.helpers.getNmapFiles(arg, recurse=options.recurse))

        # Exit if no XML files found
        if nmapXmlFilenames == []:
            print('No Nmap XML files found.\n')
            parser.print_help()
            sys.exit(1)

        portFilter = []
        serviceFilter = []
        filters = NmapFilters()
        if not options.interactive:
            # Check if only specific ports should be parsed
            if options.ports:
                portFilter = list(map(int, options.ports.split(',')))
                filters.ports = portFilter
                self.lamePrint.hprint('Set port filter to %s' % portFilter)

            # Check if only specific ports should be parsed
            if options.svcFilter:
                serviceFilter = options.svcFilter.split(',')
                filters.services = serviceFilter
                self.lamePrint.hprint(
                    'Set service filter to %s' % serviceFilter)

        # Parse nmap files
        nmapOutput = NmapOutput(nmapXmlFilenames)
        # Output successfully loaded and any failed files
        self.helpers.printImportSummary(nmapOutput, False)

        # Print import summary if requested
        if options.importedFiles:
            self.lamePrint.header("Import Summary")
            self.helpers.printImportSummary(nmapOutput, True)

        # Check if default flags were used
        defaultFlags = not options.ipList and not options.aliveHosts and not options.servicelist and not options.verbose and not options.cmd and not options.combine and not options.uniquePorts and not options.importedFiles

        if options.combine:
            nmapOutput.generateNmapParseXml(options.combine)

        if not options.interactive:
            if (defaultFlags):
                defaultFilters = NmapFilters()
                defaultFilters.onlyAlive = False
                defaultFilters.mustHavePorts = False
                self.helpers.printHosts(nmapOutput, filters=defaultFilters)
                self.helpers.printUniquePorts(
                    nmapOutput.getHostDictionary(), filters=defaultFilters)

            if options.ipList:
                self.helpers.printHosts(nmapOutput, filters=filters)

            if (options.uniquePorts):
                self.helpers.printUniquePorts(nmapOutput.getHostDictionary(
                    filters=filters), filters=filters)

            if options.aliveHosts:
                self.helpers.printAliveIps(nmapOutput)

            if options.servicelist or options.verbose:
                self.helpers.printServiceList(
                    nmapOutput, filters=filters, verbose=options.verbose)

            if options.cmd:
                self.helpers.executeCommands(
                    options.cmd, nmapOutput, filters=filters)

            if settings.printHumanFriendlyText and (defaultFlags or options.hostSummary):
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
