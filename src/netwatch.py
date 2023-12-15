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
#   Netwatch v3.2.0
#   by: @NCSickels

# Imports
import sys
import os
import subprocess
import threading
import requests
import random
import datetime
import glob
from time import gmtime, strftime, sleep
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from bs4 import BeautifulSoup

# Custom Imports
from modules import *
from logger import *
from themes import *

# Utility Classes


class Program:
    "A class for main program functions"

    def __init__(self):
        self.updateHandler = UpdateHandler()
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator()
        self.logger = Logger()
        self.notify = Notify()
        self.configFile = os.path.dirname(
            os.path.abspath(__file__)) + '/netwatch.ini'

    def start(self) -> None:
        self.clearScreen()
        print(Netwatch.netwatchLogo)
        self.updateHandler.checkForUpdate()
        self.createFolders([("general_config", "tooldir"),
                            ("general_config", "scandir"),
                            ("sagemode", "datadir")])

    def createFolders(self, paths: any) -> None:
        for section, option in paths:
            path = self.configManager.getPath(section, option)
            if not os.path.isdir(path):
                os.makedirs(path)

    def end(self) -> None:
        self.notify.endProgram()
        sleep(0.25)
        sys.exit()

    # TODO: Adjust color styling for the Notify class within this method
    def clean(self, path: str) -> None:
        if os.path.exists(path):
            deleted_files = False
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # self.logger.info(
                            #     f'Cleaning ~/Netwatch/src/{os.path.basename(os.path.normpath(path))}/ directory...')
                            self.notify.cleaningDirectory(path)
                            os.remove(file_path)
                            self.notify.deletingFile(file_path)
                            deleted_files = True
                        except Exception as e:
                            print(e)
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            self.notify.cleaningDirectory(path)
                            os.rmdir(dir_path)
                            deleted_files = True
                        except Exception as e:
                            print(e)
                # os.rmdir(path)
                if deleted_files:
                    self.notify.directoryCleaned(path, deleted_files)  # ✔
                else:
                    self.notify.directoryCleaned(path, deleted_files)
            else:
                raise FileNotFoundError(
                    f'{Color.RED}{path} directory not found!{Color.END}\n')
        else:
            raise FileNotFoundError(
                f'{Color.RED}Path {path} does not exist!{Color.END}\n')

    def printPath(self, module: str) -> None:
        self.notify.currentDirPath(module)

    def clearScreen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def findFiles(self, file_type: any, directory='/') -> str:
        self.logger.info(f'Searching for {file_type} files...')
        # self.notify.findFiles(file_type)  # (".ovpn")
        try:
            search_path = os.path.join(directory, '**/*'+file_type)
            files = glob.glob(search_path, recursive=True)
            if not files:
                self.logger.warning(f'No {file_type} files found.')
                # self.notify.noFilesFound(file_type)  # (".ovpn")
                return
            for filename in files:
                self.logger.info(f'Found file {filename}')
                # self.notify.foundFiles(filename)
                response = input("Use this file? [y/n]: ").lower()
                if response in ["y", "yes"]:
                    self.configManager.set(
                        "general_config", "ovpn_path", filename)
                    self.logging.info(f'Selected file {filename}')
                    # self.notify.setFiles(filename)
                    return filename
            # self.notify.noFilesFound(file_type, " other")
            self.logger.warning(
                (f'No other {file_type} files found. Please manually add path to .ini file.'))
        except Exception as e:
            # self.notify.exception(e)
            # self.notify.noFilesFound(file_type)
            self.logger.error(f'An error occurred: {e}')
            self.logger.warning(f'No {file_type} files found!')

    def __del__(self):
        # sys.stdout = self.original_stdout
        # self.log_file.close()
        pass


class CommandHandler:
    "A class for handling commands from the user"

    def __init__(self):
        self.program = Program()
        self.updateHandler = UpdateHandler()
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator()
        self.logger = Logger()

    def execute(self, command: str, module=None) -> None:
        match command:
            case "help" | "?":
                self.tableCreator.displayTableFromFile(module)
            case "update":
                self.updateHandler.checkForUpdate()
            case "clear" | "cls":
                self.program.clearScreen()
            case "clean":
                self.program.clean(self.configManager.getPath(
                    "general_config", "tooldir"))
                self.program.clean(self.configManager.getPath(
                    "general_config", "scandir"))
                self.program.clean(
                    self.configManager.getPath("sagemode", "datadir"))
                # self.completed()
            case "path" | "pwd":
                self.program.printPath(module)
            case "exit" | "quit" | "end":
                self.program.end()

    def completed(self) -> None:
        input("\nClick [return] to continue...")


# Start Menu Classes


class Netwatch:
    "A menu class for Netwatch tools"

    version = ConfigManager().get("general_config", "__version__")
    netwatchLogo = f'''
                    :!?Y5PGGPP5!:             .!JPGBGPY7^.
                  ..J#@#Y!75#@@@&P7:     .~7?5#@@&BY77YG#BY:
                  .^7~^.    .!P&@@@&BJ: .7B&@@@@G7.     :!Y!
                               :?G&@&Y: :5@&#BJ^       ..
                   !J!.   .:~!~^  :~^.   .^^:..:~!!~:  ..YJ.
                   7B~ .~5#&@@@&BJ:  .:  .. .JB&@@@@&G~  ~#!
                  .77. !#@@@@@@@@&7  ?Y  J? ^B@@@@&&&@B: :!:
                     .^JY?!~~!?PB!   5J  ?P. !BP?!^::^!!^
                    ::.         .^.~YJ:  .?Y!~:         .:.
                 .^JG~           :5?:  ..  .75^          ?G?:
               .:J&@Y            !Y   ....   ?~          :B@B~.
               ^5@@@G^       .:!J5G57.   .~YGG5?!:.     .^G@@@?
              .J&@@@@#57~~!YBB&@@@@@@BJ7JG@@@@@@@&BPJ775B#@@@&P.
               :#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@B7
               .J@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@GJ:
                .!P#&&&@@@@@@@@@&&&&@@@@@@@@&#&&@@@@@@@@@&P?^.
                   .:^^~!!!!YB@&&G5J?7!!?JYJ?JPPPPJ777!~~^.
                             :Y#@@@@&#BBBB#&@@&#J^
                               :75B&&&&@@&&&BY!:.
                                  .:::^^^^:::.
===================================================================================
       ███╗   ██╗███████╗████████╗██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗
       ████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
       ██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║███████║   ██║   ██║     ███████║
       ██║╚██╗██║██╔══╝     ██║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║
       ██║ ╚████║███████╗   ██║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║
       ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
===================================================================================
    v{version}                                      Noah Sickels (@NCSickels)
===================================================================================
'''

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.notify = Notify()
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
                print(AutoAttack.menuLogo)
                AutoAttack()
            case "1":
                print(InformationGathering.menuLogo)
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
                self.notify.unknownInput(choice)
                self.__init__()
        self.__init__()


class AutoAttack:
    "A menu class for the Automated Attack Tool for HTB, TryHackMe, etc."

    menuLogo = '''
===================================================================================
                    █████╗ ██╗   ██╗████████╗ ██████╗            
                   ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗           
                   ███████║██║   ██║   ██║   ██║   ██║           
                   ██╔══██║██║   ██║   ██║   ██║   ██║           
                   ██║  ██║╚██████╔╝   ██║   ╚██████╔╝           
                   ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝            
             █████╗ ████████╗████████╗ █████╗  ██████╗██╗  ██╗
            ██╔══██╗╚══██╔══╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝
            ███████║   ██║      ██║   ███████║██║     █████╔╝ 
            ██╔══██║   ██║      ██║   ██╔══██║██║     ██╔═██╗ 
            ██║  ██║   ██║      ██║   ██║  ██║╚██████╗██║  ██╗
            ╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
===================================================================================
'''

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.notify = Notify()
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
            # self.notify.runOvpn(os.path.basename(updatedConfigPath))
            # print(os.getenv("TERM"))
            # subprocess.Popen(["gnome-terminal", "--", "sudo", "openvpn", updatedConfigPath])
            # subprocess.run(["sudo", "openvpn", updatedConfigPath])
        except subprocess.CalledProcessError as e:
            self.logger.error(f'An error occurred: {e}')
            print("\n")
            self.logger.info("Returning to previous context menu...")
            Netwatch()


class InformationGathering:
    "A menu class for Information Gathering tools"

    menuLogo = '''
===================================================================================
                        ██╗███╗   ██╗███████╗ ██████╗ 
                        ██║████╗  ██║██╔════╝██╔═══██╗
                        ██║██╔██╗ ██║█████╗  ██║   ██║
                        ██║██║╚██╗██║██╔══╝  ██║   ██║
                        ██║██║ ╚████║██║     ╚██████╔╝
                        ╚═╝╚═╝  ╚═══╝╚═╝      ╚═════╝ 
===================================================================================
    '''

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.notify = Notify()
        self.logger = Logger()

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '

        self.run()

    def run(self) -> None:
        choiceInfo = input(self.netwatchPrompt)
        match choiceInfo:  # .strip()
            case "1":
                print(NmapMenu.nmapLogo)
                NmapMenu()
            case "2":
                Sagemode()
            case "3":
                pass
                # Currently not working
                # PortScanner()
            case "4":
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
                self.notify.unknownInput(choiceInfo)
                self.__init__()
        self.__init__()


# Bring user to main prompt first or ask for target IP first as currently implemented?
class NmapMenu:
    "A menu class for Nmap"

    nmapLogo = '''
===================================================================================
                        ███╗   ██╗███╗   ███╗ █████╗ ██████╗ 
                        ████╗  ██║████╗ ████║██╔══██╗██╔══██╗
                        ██╔██╗ ██║██╔████╔██║███████║██████╔╝
                        ██║╚██╗██║██║╚██╔╝██║██╔══██║██╔═══╝ 
                        ██║ ╚████║██║ ╚═╝ ██║██║  ██║██║     
                        ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝                                          
===================================================================================
'''

    def __init__(self):
        self.program = Program()
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.logger = Logger()
        self.notify = Notify()
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
                self.logger.info("Scan file name already exists!")
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
        self.notify.currentTarget(self.target)
        self.notify.currentScanPath(self.scanPath)
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
                    self.notify.unknownInput(choiceNmap)
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


class Sagemode:
    "An interface for using Sagemode - an OSINT tool for finding usernames"

    sagemodeLogoText = '''

███████╗ █████╗  ██████╗ ███████╗███╗   ███╗ ██████╗ ██████╗ ███████╗
██╔════╝██╔══██╗██╔════╝ ██╔════╝████╗ ████║██╔═══██╗██╔══██╗██╔════╝
███████╗███████║██║  ███╗█████╗  ██╔████╔██║██║   ██║██║  ██║█████╗  
╚════██║██╔══██║██║   ██║██╔══╝  ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  
███████║██║  ██║╚██████╔╝███████╗██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗
╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
'''
    sagemodeLogo = '''
                         @@@%%%%%@@@
                     @%##`````@`````##&@
                   @##````````@````````##@
                 @%#`````````@@@`````````#%@
                 &#``````````@@@``````````#&
                @#````@@@@@@@@@@@@@@@@@````#@
                @%@``@@@@@@@@@@@@@@@@@@@``@%@
                @%@```@@@@@@@@@@@@@@@@@```#%@
                @@# `````````@@@``````````#@@
                 &#``````````@@@``````````#&
                  @##`````````@`````````##@
                    @##```````@``````###@
                       @@#````@````#@@
                         @@@%%%%%@@@
    '''

    def __init__(self):
        self.configManager = ConfigManager()
        self.console = Console()
        self.notifySagemode = NotifySagemode
        self.notify = Notify()
        self.positive_count = 0
        self.usernamePrompt = "\nEnter target username: "
        self.username = input(self.usernamePrompt)
        self.resultDir = self.configManager.getPath("sagemode", "datadir")
        self.result_file = self.resultDir + self.username + ".txt"
        self.found_only = False
        self.__version__ = "1.1.3"

        self.start(self.sagemodeLogo, self.sagemodeLogoText, delay=0.001)

    def printLogo(self) -> None:
        for line in self.sagemodeLogo.split("\n"):
            for character in line:
                if character in ["█"]:
                    rprint(f"[yellow]{character}", end="", flush=True)
                else:
                    rprint(f"[bright_red]{character}", end="", flush=True)
            print()
    # this function checks if the url not a false positive result, return false

    def is_soft404(self, html_response: str) -> bool:
        soup = BeautifulSoup(html_response, "html.parser")
        page_title = soup.title.string.strip() if soup.title else ""
        for error_indicator in soft404_indicators:
            if (
                # check if the error indicator is in the html string response
                error_indicator.lower() in html_response.lower()
                # check for the title bar of the page if there are anyi error_indicator
                or error_indicator.lower() in page_title.lower()
                # Specific check sites, since positive result will have the username in the title bar.
                or page_title.lower() == "instagram"
                # patreon's removed user
                or page_title.lower() == "patreon logo"
                or "sign in" in page_title.lower()
            ):
                return True
        return False

    def check_site(self, site: str, url: str, headers):
        url = url.format(self.username)
        # we need headers to avoid being blocked by requesting the website 403 error
        try:
            with requests.Session() as session:
                response = session.get(url, headers=headers)
                # Raises an HTTPError for bad responses
            # further check to reduce false positive results
            if (
                response.status_code == 200
                and self.username.lower() in response.text.lower()
                and not self.is_soft404(response.text)
            ):
                # to prevent multiple threads from accessing/modifying the positive
                # counts simultaneously and prevent race conditions.
                with threading.Lock():
                    self.positive_count += 1
                self.console.print(self.notifySagemode.found(site, url))
                with open(self.result_file, "a") as f:
                    f.write(f"{url}\n")
            # the site reurned 404 (user not found)
            else:
                if not self.found_only:
                    self.console.print(self.notifySagemode.not_found(site))
        except Exception as e:
            self.notifySagemode.exception(site, e)

    def start(self, bannerText: str, bannerLogo: str, delay=0.001):
        """
        Parameters:
            banner
            delay=0.2
        """
        for line in bannerLogo.split("\n"):
            for character in line:
                if character in ["█"]:
                    rprint(f"[yellow]{character}", end="", flush=True)
                else:
                    rprint(f"[bright_red]{character}", end="", flush=True)
            print()
        for line in bannerText.split("\n"):
            for character in line:
                if character in ["#", "@", "%", "&"]:
                    rprint(f"[yellow]{character}", end="", flush=True)
                else:
                    rprint(f"[bright_red]{character}", end="", flush=True)
            print()

        """
        Start the search.
        """
        self.console.print(self.notifySagemode.start(
            self.username, len(sites)))

        current_datetime = datetime.datetime.now()
        date = current_datetime.strftime("%m/%d/%Y")
        time = current_datetime.strftime("%I:%M %p")
        headers = {"User-Agent": random.choice(user_agents)}

        with open(self.result_file, "a") as file:
            file.write(f"\n\n{29*'#'} {date}, {time} {29*'#'}\n\n")

        # keep track of thread objects.
        threads = []

        try:
            with self.console.status(
                f"[*] Searching for target: {self.username}", spinner="bouncingBall"
            ):
                for site, url in sites.items():
                    # creates a new thread object
                    thread = threading.Thread(
                        target=self.check_site, args=(site, url, headers))
                    # track the thread objects by storing it in the assigned threads list.
                    threads.append(thread)
                    # initiate the execution of the thread
                    thread.start()
                for thread in threads:
                    # waits for each thread to finish before proceeding.
                    # to avoid output problems and maintain desired order of executions
                    thread.join()

            # notify how many sites the username has been found
            self.console.print(
                self.notifySagemode.positive_res(
                    self.username, self.positive_count)
            )
            # notify where the result is stored
            self.console.print(
                self.notifySagemode.stored_result(self.result_file))
            self.notify.previousContextMenu("Information Gathering")
            InformationGathering()

        except Exception:
            self.console.print_exception()


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
