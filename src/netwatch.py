#!/usr/bin/env python3
#
#
# ███╗   ██╗███████╗████████╗██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗
# ████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
# ██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║███████║   ██║   ██║     ███████║
# ██║╚██╗██║██╔══╝     ██║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║
# ██║ ╚████║███████╗   ██║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║
# ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
#
#
#   Netwatch v3.2.6
#   by: @NCSickels

# Imports
import sys
import os
import subprocess
from time import gmtime, strftime, sleep
from bs4 import BeautifulSoup

# Custom Imports
from modules import *
from logger import *
from themes import *


# Start Menu Classes
class Netwatch:
    """A menu class for Netwatch tools"""

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.tableCreator = TableCreator()
        self.logger = Logger()

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '
        self.toolDir = self.configManager.getPath('general_config', 'tooldir')
        self.scanDir = self.configManager.getPath('general_config', 'scandir')
        self.storeHistory = self.configManager.getbool(
            'general_config', 'storehistory')

        self.run()

    def run(self) -> None:
        choice = input(self.netwatchPrompt)
        match choice:  # .strip()
            case "0":
                print(AUTOATTACK_LOGO)
                AutoAttack()
            case "1":
                print(INFO_LOGO)
                InformationGathering()
            case "?" | "help":
                [self.commandHandler.execute(choice, module)
                    for module in ["Main", "Core"]]
            case "update":
                self.commandHandler.execute(choice)
            case "\r" | "\n" | "" | " " | "back":
                pass
            case "clear" | "cls":
                self.commandHandler.execute(choice)
            case "clean":
                self.commandHandler.execute(choice)
            case "path" | "pwd":
                self.commandHandler.execute(choice, "Netwatch")
            case "exit" | "quit" | "end":
                self.commandHandler.execute(choice)
            case _:
                self.logger.warning("Unknown input. Type '?' for help.")
                self.__init__()
        self.__init__()


class AutoAttack:
    """A menu class for the Automated Attack Tool for HTB, TryHackMe, etc."""

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.logger = Logger()
        self.tableCreator = TableCreator()
        self.run()

    def run(self) -> None:
        self.program.clearScreen()
        updatedConfigPath = self.program.findFiles(
            '.ovpn', os.path.expanduser('~'))
        # Run .ovpn file if found
        # Check for default value in config file
        if updatedConfigPath:
            self.startOvpn(updatedConfigPath)

    def startOvpn(self, updatedConfigPath: str) -> None:
        try:
            self.logger.info('Starting OpenVPN profile...')
            # print(os.getenv("TERM"))
            # subprocess.Popen(["gnome-terminal", "--", "sudo", "openvpn", updatedConfigPath])
            # subprocess.run(["sudo", "openvpn", updatedConfigPath])
        except subprocess.CalledProcessError as e:
            self.logger.error(f'An error occurred: {e}')
            print("\n")
            self.logger.info("Returning to previous context menu...")
            Netwatch()


class InformationGathering:
    """A menu class for Information Gathering tools"""

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.logger = Logger()

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '

        self.run()

    def run(self) -> None:
        choiceInfo = input(self.netwatchPrompt)
        match choiceInfo:  # .strip()
            case "1":
                print(NMAP_LOGO)
                NmapMenu()
            case "2":
                print(PYDISCOVER_LOGO)
                PyDiscover()
            case "3":
                SagemodeMenu()
            case "4":
                pass
                # Currently not working
                # PortScanner()
            case "5":
                pass
                # print(Host2IP.host2ipLogo)
                # Host2IP()
            case "?" | "help":
                [self.commandHandler.execute(choiceInfo, choice) for choice in [
                    "Information_Gathering", "Core"]]
            case "clear" | "cls":
                self.commandHandler.execute(choiceInfo)
            case "clean":
                self.commandHandler.execute(choiceInfo)
            case "path" | "pwd":
                self.commandHandler.execute(
                    choiceInfo, "Netwatch/Information_Gathering")
            case "exit" | "quit" | "end":
                self.commandHandler.execute(choiceInfo)
            case "back":
                self.logger.info("Returning to previous context menu...")
                Netwatch()
            case _:
                self.logger.warning("Unknown input. Type '?' for help.")
                self.__init__()
        self.__init__()


# Bring user to main prompt first or ask for target IP first as currently implemented?
class NmapMenu:
    """A Netwatch interface for using Nmap."""

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.logger = Logger()
        self.nmap = Nmap()
        self.netwatchPrompt = "netwatch ~# "
        self.gitRepo = "https://github.com/nmap/nmap.git"
        self.targetPrompt = "\nEnter target IP: "
        self.scanFileNamePrompt = "\nEnter scan file name: "
        self.target = None
        self.scanPath = None

        self.run()

    def run(self):
        if self.nmap.checkForNmap():
            # try:
            self.target = input(self.targetPrompt)
            self.scanPath = "nmap-" + "-" + \
                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
            if os.path.isfile(self.scanPath):
                self.logger.info("File name already exists!")
                self.logger.info("Would you like to overwrite this file?")
                response = input("[y/n]: ")
                if response.lower() in ["y", "yes"]:
                    self.menu()
            else:
                self.program.clearScreen()
                self.menu()
        else:
            self.logger.error(
                "Nmap could not be installed. Returning to previous main menu...")
            Netwatch()

    def menu(self) -> None:
        print(self.nmapLogo)
        self.logger.info("Scan Path -> " + self.scanPath)
        try:
            choiceNmap = input(self.netwatchPrompt)
            match choiceNmap:
                case "default" | "default scan" | "defaultscan":
                    self.nmap.scan(self.target, self.scanPath, "default_scan")
                    self.getInput()
                case "quick scan" | "quick" "quickscan":
                    self.nmap.scan(self.target, self.scanPath, "quick_scan")
                    self.getInput()
                case "intense scan" | "intense" | "intensescan":
                    self.nmap.scan(self.target, self.scanPath, "intense_scan")
                    self.getInput()
                case "vuln" | "vuln scan" | "vulnscan" | "vulnerability" | "vulnerability scan":
                    self.nmap.scan(self.target, self.scanPath, "vuln_scan")
                    self.getInput()
                case _ if choiceNmap.startswith("set "):
                    self.setParameters(choiceNmap)
                case "?" | "help":
                    [self.commandHandler.execute(choiceNmap, choice) for choice in [
                        "Nmap_Scans", "Nmap_Commands", "Core"]]
                case "clear" | "cls":
                    self.commandHandler.execute(choiceNmap, "Nmap")
                case "clean":
                    self.commandHandler.execute(choiceNmap, "Nmap")
                case "path" | "pwd":
                    self.commandHandler.execute(
                        choiceNmap, "Netwatch/Information_Gathering/Nmap")
                    self.menu()
                # case "exit" | "quit" | "end":
                #     self.program.end()
                case "back":
                    self.logger.info("Returning to previous context menu...")
                    InformationGathering()
                case _:
                    self.logger.warning("Unknown input. Type '?' for help.")
                    self.menu()
            self.menu()
        except Exception as e:
            print("\n")
            self.logger.info("Returning to main menu...")
            Netwatch()

    def getInput(self):
        response = self.nmap.promptForInput(
            "Would you like to run another scan? [y/n]: ")
        if response.lower() in ["y", "yes"]:
            self.run()
        else:
            self.logger.info("Returning to main menu...")
            Netwatch()

    # update scan file after using set target?
    def setParameters(self, input: str) -> None:
        # _, param, value = input.split(" ", 2)
        parts = input.split(" ")
        if len(parts) < 3:
            self.logger.error("Invalid syntax! Usage: 'set <param> <value>'")
            return
            # self.menu(target, scanPath)
        _, param, value = parts
        if param == "target":
            self.target = value
        elif param == "log" | "scan":
            scanName, _, self.scanPath = value.partition(" ")
            if not self.scanPath:
                self.scanPath = "nmap-" + scanName + "-" + \
                    strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
            self.scanPath = "nmap-" + scanName + "-" + \
                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
        self.menu()


class PyDiscover:
    """A Python network discovery tool based on Netdiscover."""

    def __init__(self) -> None:
        pass


class SagemodeMenu:
    """A Netwatch interface for using Sagemode - an OSINT tool for finding usernames"""

    def __init__(self):
        self.sagemode = Sagemode()
        self.run()

    def run(self):
        self.sagemode.start(SAGEMODE_LOGO,
                            SAGEMODE_LOGO_TEXT, delay=0.001)


def main():
    try:
        # TODO: Fix alternate themes not working
        themes.set_theme("DefaultTheme")
        program = Program()
        program.start()
        Netwatch()
    except KeyboardInterrupt:
        sleep(0.25)
        sys.exit()


if __name__ == "__main__":
    main()
