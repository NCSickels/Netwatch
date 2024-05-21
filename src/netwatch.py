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
import threading
import requests
import random
import datetime
import glob
from time import gmtime, strftime, sleep
from bs4 import BeautifulSoup

# Custom Imports
from modules import *
from logger import *
from themes import *


# Utility Classes
class Program:
    """A class for main program functions"""

    def __init__(self):
        self.updateHandler = UpdateHandler()
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator()
        self.logger = Logger()
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
        print("\n Bye.\n")
        sleep(0.25)
        sys.exit()

    def clean(self, path: str) -> None:
        _full_path = os.path.basename(os.path.normpath(path))
        self.logger.info('Cleaning directories...')
        if os.path.exists(path):
            deleted_files = False
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            self.logger.info(f'Deleted file: {file_path}')
                            deleted_files = True
                        except Exception as e:
                            print(e)
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            os.rmdir(dir_path)
                            deleted_files = True
                        except Exception as e:
                            print(e)
                # os.rmdir(path)
                if deleted_files:
                    self.logger.info(
                        f'Directory:{_full_path} successfully cleaned.')
                else:
                    self.logger.info(f'No files found in {_full_path}.')
            else:
                raise FileNotFoundError(
                    f'{Color.RED}{path} directory not found!{Color.END}\n')
        else:
            raise FileNotFoundError(
                f'{Color.RED}Path {path} does not exist!{Color.END}\n')

    def printPath(self, module: str) -> None:
        _split_module = module.split("/")
        if (len(_split_module) <= 1):  # if module is in root directory (Netwatch/)
            print(f'\n[*] Module -> {_split_module[0]}')
            print(f'[*] Path   -> {module+"/"}\n')
            # self.logger.info(
            #     f'Module -> {_split_module[0]}\n')
            # self.logger.info(f'Path   -> {module+"/"}')
        else:
            print(f'\n[*] Module -> {_split_module[len(_split_module)-1]}')
            print(f'[*] Path   -> {module+"/"}\n')
            # self.logger.info(
            #     f'\nModule -> {_split_module[len(_split_module)-1]}')
            # self.logger.info(f'Path   -> {module+"/"}')

    def clearScreen(self) -> None:
        print("\033[H\033[J", end="")
        # os.system('cls' if os.name == 'nt' else 'clear')

    def findFiles(self, file_type: any, directory='/') -> str:
        self.logger.info(f'Searching for {file_type} files...')
        try:
            search_path = os.path.join(directory, '**/*'+file_type)
            files = glob.glob(search_path, recursive=True)
            if not files:
                self.logger.warning(f'No {file_type} files found.')
                return
            for filename in files:
                self.logger.info(f'Found file {filename}')
                response = input("Use this file? [y/n]: ").lower()
                if response in ["y", "yes"]:
                    self.configManager.set(
                        "general_config", "ovpn_path", filename)
                    self.logging.info(f'Selected file {filename}')
                    return filename
            self.logger.warning(
                (f'No other {file_type} files found. Please manually add path to .ini file.'))
        except Exception as e:
            self.logger.error(f'An error occurred: {e}')
            self.logger.warning(f'No {file_type} files found!')

    def __del__(self):
        # sys.stdout = self.original_stdout
        # self.log_file.close()
        pass


# Start Menu Classes
class Netwatch:
    """A menu class for Netwatch tools"""

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
                self.logger.warning("Unknown input. Type '?' for help.")
                self.__init__()
        self.__init__()


class AutoAttack:
    """A menu class for the Automated Attack Tool for HTB, TryHackMe, etc."""

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
                print(PyDiscover.pydiscoverLogoText)
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

    pydiscoverLogoText = '''

██████╗ ██╗   ██╗██████╗ ██╗███████╗ ██████╗ ██████╗ ██╗   ██╗███████╗██████╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██║██╔════╝██╔════╝██╔═══██╗██║   ██║██╔════╝██╔══██╗
██████╔╝ ╚████╔╝ ██║  ██║██║███████╗██║     ██║   ██║██║   ██║█████╗  ██████╔╝
██╔═══╝   ╚██╔╝  ██║  ██║██║╚════██║██║     ██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗
██║        ██║   ██████╔╝██║███████║╚██████╗╚██████╔╝ ╚████╔╝ ███████╗██║  ██║
╚═╝        ╚═╝   ╚═════╝ ╚═╝╚══════╝ ╚═════╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝
'''

    def __init__(self) -> None:
        pass


class SagemodeMenu:
    """A Netwatch interface for using Sagemode - an OSINT tool for finding usernames"""

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
        self.sagemode = Sagemode()
        self.run()

    def run(self):
        self.sagemode.start(self.sagemodeLogo,
                            self.sagemodeLogoText, delay=0.001)


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
