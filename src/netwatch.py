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
#   Netwatch v2.2.1
#   by: @NCSickels

# Imports
import sys
import os
import configparser
import json
import socket
import re
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

from sites import sites, soft404_indicators, user_agents


# Common Functions

class Color:
    "A class for colorizing terminal output"
    HEADER = '\033[95m'
    IMPORTANT = '\33[35m'
    NOTICE = '\033[33m'
    BLUE = '\033[34m'  # [1;34m]
    OKBLUE = '\033[94m'
    GREEN = '\033[32m'  # [1;32m]
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    LOGGING = '\33[34m'

# TODO: Generalize this class for use in other modules


class Notify:
    "A helper class for notifications of Netwatch process"

    def __init__(self):
        self.console = Console()

    # Methods for Netwatch & General Use

    def update(self, remoteVersion: str, localVersion: str) -> str:
        self.console.print(
            f"[red][[bright_red]![red]] [yellow]Update Available!\n[/yellow]"
            + f"[red][[yellow]![red]] [bright_yellow]You are running Version: [bright_green]{localVersion}\n"
            + f"[red][[/red][yellow]![red]][bright_yellow] New Version Available: [bright_green]{remoteVersion}"
        )

    def upToDate(self) -> str:
        self.console.print(
            f"[red][[yellow]![red]] [bright_yellow]Netwatch is up to date.\n")

    def endProgram(self) -> None:
        self.console.print(
            f"\n[bright_yellow]Finishing up...\n")

    def previousContextMenu(self, module: str) -> None:
        self.console.print((f"\n[bright_yellow]Returning to "
                            f"[bright_blue]{module} [bright_yellow]menu...\n"))

    def unknownInput(self, choice: str) -> str:
        self.console.print(
            f"[bright_red][[bright_red]![bright_red]] [bright_yellow]Unknown input: [bright_red]{choice}. [bright_yellow]Type [bright_red]'?' [bright_yellow]for help.")

    def cleaningDirectory(self, path: str) -> None:
        self.console.print(
            f"\n[red][[yellow]![red]] [bright_yellow]Cleaning [bright_blue]{path} [bright_yellow]directory...")

    def currentDirPath(self, module: any, path=None) -> None:
        split_module = module.split("/")
        if (len(split_module) <= 1):    # if module is in root directory (Netwatch/)
            self.console.print(
                f"\n[black][[red]*[black]] [bright_yellow]Module [bright_black]-> [bright_red]{split_module[0]}\n[black][[red]*[black]] [bright_yellow]Path [bright_black]  -> [bright_red]{module+'/'}\n")
        else:
            self.console.print(
                f"\n[black][[red]*[black]] [bright_yellow]Module [bright_black]-> [bright_red]{split_module[len(split_module)-1]}\n[black][[red]*[black]] [bright_yellow]Path [bright_black]  -> [bright_red]{module+'/'}\n")

    def updateScriptError(self, error: str):
        self.console.print(
            f"[bright_red][[bright_red]![bright_red]] [bright_yellow]A problem occured while updating: [bright_red]{error}")

    def exception(self, error: str):
        self.console.print(
            f"[black][[red]![black]] [bright_yellow]An error occurred: [bright_red]{error}...")

    # Methods for InformationGathering
    # Methods for Nmap

    def currentTarget(self, target: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Target [bright_black]-> [bright_red]{target}")

    def currentLogPath(self, logPath: str) -> None:
        self.console.print(
            f"[black][[red]*[black]] [bright_yellow]Log Path [bright_black]-> [bright_red]{logPath}\n")

    def scanCompleted(self, logPath: str) -> None:
        self.console.print(
            f'\n[bright_green][✔] Scan completed, log saved to: [bright_blue]{logPath}')


class NotifySagemode:
    "A helper class for notifications of Sagemode process"

    @staticmethod
    def start(username: str, number_of_sites: any) -> str:
        if username or sites is not None:
            return f"[yellow][[bright_red]*[yellow][yellow]] [bright_blue]Searching {number_of_sites} sites for target: [bright_yellow]{username}"

    # notify the user how many sites the username has been found
    @staticmethod
    def positive_res(username: str, count) -> str:
        return f"\n[yellow][[bright_red]+[yellow]][bright_green] Found [bright_red]{username} [bright_green]on [bright_magenta]{count}[bright_green] sites"

    # notify the user where the result is stored
    @staticmethod
    def stored_result(result_file: str) -> str:
        return f"[bright_green][[yellow]@[bright_green]] [orange3]Results stored in: [bright_green]{result_file}\n"

    @staticmethod
    def not_found(site: str, status_code="") -> str:
        if status_code:
            return f"[black][[red]-[black]] [blue]{site}: [yellow]Not Found! {status_code}"
        return f"[black][[red]-[black]] [blue]{site}: [yellow]Not Found!"

    @staticmethod
    def found(site: str, url: str) -> str:
        return f"[red][[green]+[red]] [green]{site}: [blue]{url}"

    @staticmethod
    def update(local_version: str, remote_version: str) -> str:
        return (
            "[red][[bright_red]![red]] [yellow]Update Available!\n[/yellow]"
            + f"[red][[yellow]![red]] [bright_yellow]You are running Version: [bright_green]{local_version}\n"
            + f"[red][[/red][yellow]![red]][bright_yellow] New Version Available: [bright_green]{remote_version}"
        )

    @staticmethod
    def update_error(error: str) -> str:
        return f"[bright_red][[bright_red]![bright_red]] [bright_yellow]A problem occured while checking for an update: [bright_red]{error}"

    @staticmethod
    def version(version: str) -> str:
        return f"[bright_yellow]Sagemode [bright_red]{version}"

    @staticmethod
    def exception(site, error: str) -> str:
        return f"[black][[red]![black]] [blue]{site}: [bright_red]{error}..."


class CommandHistory:
    def __init__(self):
        self.configManager = ConfigManager()
        self.storeHistory = self.configManager.getbool(
            'general_config', 'storeHistory')
        self.logDir = self.configManager.getPath('general_config', 'logDir')
        self.history = []  # set()

    def update(self, command: str) -> None:
        self.history.append(command)
        if self.storeHistory:
            with open(self.logDir + "/command_history-" + strftime("%Y-%m-%d_%H:%M", gmtime()), 'a') as history_log:
                history_log.write(f"{command}\n")

    def print(self) -> None:
        print("\n" + "\n".join(f"{i}  {command}" for i,
              command in enumerate(self.history, start=1)) + "\n")

    def clear(self) -> None:
        self.history.clear()
        print(f'\n{Color.OKGREEN}[✔] Command history cleared.{Color.END}\n')

    def save(self) -> None:
        if self.storeHistory:
            with open(self.logDir + "/command_history-" + strftime("%Y-%m-%d_%H:%M", gmtime()), 'a') as history_log:
                for i, command in enumerate(self.history, start=1):
                    history_log.write(f"{i}  {command}\n")


class ConfigManager:
    "A class for managing configuration files"

    def __init__(self):
        self.config = configparser.ConfigParser()
        configFile = os.path.dirname(
            os.path.abspath(__file__)) + '/netwatch.cfg'
        self.config.read(configFile)
        self.installDir = os.path.dirname(os.path.abspath(__file__)) + '/'

    def get(self, section: any, option: any) -> str:
        return self.config.get(section, option)

    def getPath(self, section: any, option: any) -> str:
        return self.installDir + self.config.get(section, option)

    def getbool(self, section: str, option: str) -> bool:
        return self.config.getboolean(section, option)


class CommandHandler:
    def __init__(self):
        self.program = Program()
        self.updateHandler = UpdateHandler()
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator(self.configManager)
        self.notify = Notify()

    def execute(self, command: str, module=None) -> None:
        # TODO: Implement 'cd' function
        match command:
            case "help" | "?":
                self.tableCreator.displayTableFromFile(module)
            case "update":
                self.updateHandler.checkForUpdate()
                # try:
                #     subprocess.check_call(["../scripts/update.sh"], shell=True)
                # except subprocess.CalledProcessError as e:
                #     self.notify.updateScriptError(e)
            case "clear" | "cls":
                self.program.clearScr()
            case "clean":
                self.program.clean(self.configManager.getPath(
                    "general_config", "toolDir"))
                self.program.clean(self.configManager.getPath(
                    "general_config", "logDir"))
                self.program.clean(
                    self.configManager.getPath("sagemode", "dataDir"))
                self.completed()
            case "path" | "pwd":
                self.program.printPath(module)
            case "exit" | "quit" | "end":
                self.program.end()

    def completed(self) -> None:
        input("\nClick [return] to continue...")


class Program:
    "A class for main program functions"

    def __init__(self):
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator(self.configManager)
        self.notify = Notify()
        self.configFile = os.path.dirname(
            os.path.abspath(__file__)) + '/netwatch.cfg'
        self.updateHandler = UpdateHandler()
        # self.original_stdout = sys.stdout
        # self.log_file = open('typescript.log', 'w')
        # sys.stdout = self.log_file

    def start(self) -> None:
        self.clearScr()
        print(Netwatch.netwatchLogo)
        self.updateHandler.checkForUpdate()
        self.createFolders()

    def createFolders(self) -> None:
        if not os.path.isdir(self.configManager.getPath("general_config", "toolDir")):
            os.makedirs(self.configManager.getPath(
                "general_config", "toolDir"))
        if not os.path.isdir(self.configManager.getPath("general_config", "logDir")):
            os.makedirs(self.configManager.getPath("general_config", "logDir"))
        if not os.path.isdir(self.configManager.getPath("sagemode", "dataDir")):
            os.makedirs(self.configManager.getPath("sagemode", "dataDir"))

    def end(self) -> None:
        self.notify.endProgram()
        sleep(0.25)
        sys.exit()

    def clean(self, path: str) -> None:
        if os.path.exists(path):
            deleted_files = False
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            self.notify.cleaningDirectory(path)
                            os.remove(file_path)
                            print(f'\t - Deleting {file_path} file...')
                            deleted_files = True
                        except Exception as e:
                            print(e)
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            self.notify.cleaningDirectory(path)
                            os.rmdir(dir_path)
                            print(f'\t - Deleting {dir_path} directory...')
                            deleted_files = True
                        except Exception as e:
                            print(e)
                # os.rmdir(path)
                if deleted_files:
                    print(
                        f'\n{Color.OKGREEN}[✔] {path} directory successfully cleaned.{Color.END}\n')
                else:
                    print((f'\n{Color.OKGREEN}[✔] No files or directories found in'
                           f'{path}.{Color.END}\n'))
            else:
                raise FileNotFoundError(
                    f'{Color.RED}{path} directory not found!{Color.END}\n')
        else:
            raise FileNotFoundError(
                f'{Color.RED}Path {path} does not exist!{Color.END}\n')

    def printPath(self, module: str) -> None:
        self.notify.currentDirPath(module)

    def clearScr(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def find_ovpn_files(self, directory='/') -> None:
        search_path = os.path.join(directory, '**/*.ovpn')
        for filename in glob.glob(search_path, recursive=True):
            print(f'Found .ovpn file: {filename}')

    def __del__(self):
        # sys.stdout = self.original_stdout
        # self.log_file.close()
        pass


class UpdateHandler:
    def __init__(self):
        self.configManager = ConfigManager()
        self.notify = Notify()
        self.console = Console()

        self.local_version = self.configManager.get(
            "general_config", "__version__")

    def checkForUpdate(self) -> None:
        try:
            r = requests.get(
                "https://raw.githubusercontent.com/NCSickels/Netwatch/main/src/netwatch.cfg")
            matches = re.findall('__version__\s*=\s*([\d.]+)', r.text)
            if matches:
                remote_version = str(matches[0])
            else:
                pass
                raise ValueError(
                    "Unable to find version number in netwatch.cfg")

            if self.is_newer_version(remote_version, self.local_version):
                self.notify.update(remote_version, self.local_version)
                self.promptForUpdate()
            else:
                self.notify.upToDate()
        except Exception as error:
            self.notify.updateScriptError(error)

    def promptForUpdate(self) -> None:
        response = input(
            "\nWould you like to update Netwatch? [y/n]: ").lower()
        if response in ["y", "yes"]:
            self.update()
        else:
            pass
            # print(Netwatch.netwatchLogo)
            # Netwatch()

    def is_newer_version(self, remote_version: str, local_version: str) -> bool:
        remote_version_revisions = list(map(int, remote_version.split('.')))
        local_version_revisions = list(map(int, local_version.split('.')))
        return remote_version_revisions > local_version_revisions

    def update(self) -> None:
        repo_dir = os.path.dirname(os.path.realpath(__file__))
        # ensure we're performing git command in the local git repo directory
        os.chdir(repo_dir)
        subprocess.run(["git", "pull"])


class BannerPrinter:
    "A class for printing banners"

    def __init__(self, logo: str):
        self.logo = logo
        self.rich_colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'bright_black',
                            'bright_red', 'bright_green', 'bright_yellow', 'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white']
        self.print()

    def print(self) -> None:
        for line in self.logo.split("\n"):
            for character in line:
                rprint(
                    f'[{random.choice(self.rich_colors)}]{character}',
                    end="",
                    flush=True
                )
            print()

# TODO: Add a default case for global commands, and ability to specify which help menu to display, regardless of currnet module path


class TableCreator:
    def __init__(self, configManager, jsonFile=None):
        self.configManager = configManager
        self.console = Console()
        self.jsonFile = os.path.dirname(os.path.abspath(
            __file__)) + '/' + configManager.get('general_config', 'menuDataPath')

    @staticmethod
    def readJson(file_path: str) -> dict:
        with open(file_path) as f:
            data = json.load(f)
            return data

    def createTable(self, header_data: dict, column_data: list, row_data: list, column_keys: list) -> None:
        table = Table(
            show_header=header_data.get("show_header", True),
            header_style=header_data.get("header_style", "bold white"),
            title=header_data.get("title", ""),
            width=int(header_data.get("width", 84)),
            show_lines=True)
        for i, column in enumerate(column_data):
            table.add_column(
                column.get("title", ""),
                style=column.get("style", ""),
                justify=column.get("justify", "right"),
                width=column.get("width", 30))
        column_keys += [None] * (len(column_data) - len(column_keys))
        for row in row_data:
            row_values = [str(row.get(column_keys[i], ""))
                          for i in range(len(column_data))]
            table.add_row(*row_values)
        return table

    def displayTable(self, jsonData: dict, module: str) -> None:
        column_keys_dict = {
            "Main": ["option", "modules", "description"],
            "Core": ["command", "description"],
            "Information_Gathering": ["option", "modules", "description"],
            "Nmap_Scans": ["type", "options", "description"],
            "Nmap_Commands": ["command", "description"],
        }
        for table in jsonData[module]:
            header_data = table.get("header", [{}])[0]
            column_data = table.get("columns", [])
            row_data = table.get("rows", [])
            column_keys = column_keys_dict.get(module, [])
            table = self.createTable(
                header_data, column_data, row_data, column_keys)
            self.console.print(table)
            print("\n")

    def displayTableFromFile(self, module: str) -> None:
        jsonData = self.readJson(self.jsonFile)
        self.displayTable(jsonData, module)

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
===================================================================================\n
'''

    def __init__(self):
        self.program = Program()  # Program(config, configFile)
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.notify = Notify()
        self.tableCreator = TableCreator(self.configManager)

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '
        self.toolDir = self.configManager.getPath('general_config', 'toolDir')
        self.logDir = self.configManager.getPath('general_config', 'logDir')
        self.storeHistory = self.configManager.getbool(
            'general_config', 'storeHistory')

        self.run()

    def run(self) -> None:
        # self.program.find_ovpn_files(os.path.expanduser('~'))
        choice = input(self.netwatchPrompt)
        match choice:
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

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '

        self.run()

    def run(self) -> None:
        choiceInfo = input(self.netwatchPrompt)
        match choiceInfo:
            case "1":
                print(Nmap.nmapLogo)
                Nmap()
            case "2":
                Sagemode()
            case "3":
                pass
                # Currently not working
                # PortScanner()
            case "4":
                print(Host2IP.host2ipLogo)
                Host2IP()
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
                self.notify.previousContextMenu("Netwatch")
                Netwatch()
            case _:
                self.notify.unknownInput(choiceInfo)
                self.__init__()
        self.__init__()


# Bring user to main prompt first or ask for target IP first as currently implemented?
class Nmap:
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
        self.notify = Notify()

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '
        self.nmapDir = self.configManager.getPath('nmap', 'nmapdir')
        self.gitRepo = self.configManager.get('nmap', 'gitrepository')
        self.targetPrompt = "Enter target IP: "
        self.logFileNamePrompt = "Enter log file name: "

        if not self.installed():
            self.install()
            self.run()
        else:
            self.run()

    def installed(self) -> bool:
        return any(os.path.isfile(path) for path in ["/usr/bin/nmap", "/usr/local/bin/nmap"])

    def install(self) -> None:
        print(
            f'\n{Color.WARNING}[!] Installing Nmap...{Color.END}\n')

        exitStatus = os.system("sudo apt-get install nmap")
        if exitStatus == 0:
            print(
                f'\n{Color.OKGREEN}[✔] Nmap successfully installed.{Color.END}\n')
            self.run()
        else:
            print((
                f'\n{Color.RED}[-]{Color.END} Error installing Nmap.\n'
                f'Returning to {Color.OKBLUE}Information Gathering{Color.END} menu...\n'))

    def run(self) -> None:
        try:
            target = input(self.targetPrompt)
            logPath = "nmap-" + "-" + \
                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
            if os.path.isfile(logPath):
                print(
                    f'\n{Color.WARNING}[!] Log file already exists!{Color.END}\n')
                response = input(
                    f'{Color.WARNING}[!] Would you like to overwrite the log file?{Color.END} [y/n]: ')
                if response.lower() == "y" or response.lower() == "yes":
                    self.menu(target, logPath)
                else:
                    self.run()
            self.menu(target, logPath)
        except KeyboardInterrupt:
            print("\n")
            InformationGathering()

    def menu(self, target: int, logPath: str) -> None:
        print(self.nmapLogo)
        self.notify.currentTarget(target)
        self.notify.currentLogPath(logPath)
        try:
            choiceNmap = input(self.netwatchPrompt)
            match choiceNmap:
                case "quick scan" | "quick" "quickscan":
                    self.runScan("quick", target, logPath)
                    self.notify.scanCompleted(logPath)
                    self.promptForAnotherScan(target, logPath)
                case "intense scan" | "intense" | "intensescan":
                    self.runScan("intense", target, logPath)
                    self.notify.scanCompleted(logPath)
                    self.promptForAnotherScan(target, logPath)
                case "default" | "default scan" | "defaultscan":
                    self.runScan("default", target, logPath)
                    self.notify.scanCompleted(logPath)
                    self.promptForAnotherScan(target, logPath)
                case "vuln" | "vuln scan" | "vulnscan" | "vulnerability" | "vulnerability scan":
                    self.runScan("vuln", target, logPath)
                    self.notify.scanCompleted(logPath)
                    self.promptForAnotherScan(target, logPath)
                case _ if choiceNmap.startswith("set "):
                    _, param, value = choiceNmap.split(" ", 2)
                    if param == "target":
                        target = value
                    elif param == "log":
                        logName, _, logPath = value.partition(" ")
                        if not logPath:
                            logPath = "nmap-" + logName + "-" + \
                                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
                        logPath = "nmap-" + logName + "-" + \
                            strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
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
                    self.menu(target, logPath)
                case "exit" | "quit" | "end":
                    self.program.end()
                case "back":
                    self.notify.previousContextMenu("Information Gathering")
                    InformationGathering()
                case _:
                    self.notify.unknownInput(choiceNmap)
                    self.menu(target, logPath)
            self.menu(target, logPath)
        except KeyboardInterrupt:
            print("\n")
            InformationGathering()

    def runScan(self, choice: str, target: int, logPath: str) -> None:
        scan_types = {
            'default': 'nmap -T4 -v -A -oN',
            'quick': 'nmap -T4 -F -v -oN',
            'intense': 'nmap -T4 -A -v -oN',
            'vuln': 'nmap -T4 -v -sV --script=vuln -oN'
        }
        for choice, scan_type in scan_types.items():
            if choice.startswith(choice):
                try:
                    os.system(f'\n{scan_type} {logPath} {target}')
                except Exception as e:
                    self.notify.exception(e)
                break

    def promptForAnotherScan(self, target: int, logPath: str) -> None:
        response = input(
            "\nWould you like to run another scan? [y/n]: ").lower()
        if response in ["y", "yes"]:
            self.menu(target, logPath)
        else:
            self.notify.previousContextMenu("Netwatch")
            Netwatch()


class Sagemode:
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
        self.resultDir = self.configManager.getPath("sagemode", "dataDir")
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


# TODO: Fix this function - IP address is not being passed correctly


class PortScanner:
    portScannerLogo = '''\n
===================================================================================
      ██████╗  ██████╗ ██████╗ ████████╗    ███████╗ ██████╗ █████╗ ███╗   ██╗
      ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔════╝██╔════╝██╔══██╗████╗  ██║
      ██████╔╝██║   ██║██████╔╝   ██║       ███████╗██║     ███████║██╔██╗ ██║
      ██╔═══╝ ██║   ██║██╔══██╗   ██║       ╚════██║██║     ██╔══██║██║╚██╗██║
      ██║     ╚██████╔╝██║  ██║   ██║       ███████║╚██████╗██║  ██║██║ ╚████║
      ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
===================================================================================
    '''

    def __init__(self) -> None:
        self.targetPrompt = "Enter target IP(s): "
        self.portPrompt = "Enter port(s) to scan: "
        self.logNamePrompt = "Enter log file name: "
        self.run()

    def run(self) -> None:
        try:
            target = input(self.targetPrompt)
            port = input(self.portPrompt)
            logName = input(self.logNamePrompt)
            logPath = "portScan-" + logName + "-" + \
                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"

            ipList = [self.ip2Int(ipAddr.strip())
                      for ipAddr in target.split(',')]
            portList = [port.strip() for port in port.split(',')]

            print(f'\n{Color.OKBLUE}[*]{Color.END} Target(s) -> ', end='')
            for ip in ipList:
                print(f'{ip}, ', end='')
            print('\n')
            print(f'{Color.OKBLUE}[*]{Color.END} Port(s)   -> ', end='')
            for port in portList:
                print(f'{port}, ', end='')
            print('\n')
            print(
                f'{Color.OKBLUE}[*]{Color.END} Log Path  -> {logPath}\n')
            self.scan(ipList, portList)
        except KeyboardInterrupt:
            print("\n")
            InformationGathering()

    def scan(self, ipList: list, portList: list) -> None:
        try:
            for ipAddr in ipList:
                for port in portList:
                    try:
                        sock = socket.socket(
                            socket.AF_INET, socket.SOCK_STREAM)
                        socket.setdefaulttimeout(1)
                        result = sock.connect_ex((ipAddr, int(port)))
                        if result == 0:
                            print(
                                f'{Color.OKGREEN}[✔]{Color.END} Discovered open port {port} on {ipAddr}')
                        else:
                            pass
                        sock.close()
                    except KeyboardInterrupt:
                        print(f'{Color.RED}[-]{Color.END} Exiting program.')
                        sys.exit()
                    except socket.gaierror:
                        print(
                            f'{Color.RED}[-]{Color.END} Hostname could not be resolved.')
                        sys.exit()
                    except socket.error:
                        print(
                            f'{Color.RED}[-]{Color.END} Could not connect to server.')
                        sys.exit()
        except KeyboardInterrupt:
            print("\n")
            InformationGathering()

    def ip2Int(self, ip: str) -> int:
        octets = ip.split('.')
        return ((int(octets[0]) << 24) + (int(octets[1]) << 16) +
                (int(octets[2]) << 8) + int(octets[3]))


class Host2IP:
    host2ipLogo = '''\n
===================================================================================
              ██╗  ██╗ ██████╗ ███████╗████████╗██████╗ ██╗██████╗ 
              ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝╚════██╗██║██╔══██╗
              ███████║██║   ██║███████╗   ██║    █████╔╝██║██████╔╝
              ██╔══██║██║   ██║╚════██║   ██║   ██╔═══╝ ██║██╔═══╝ 
              ██║  ██║╚██████╔╝███████║   ██║   ███████╗██║██║     
              ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝╚═╝╚═╝     
===================================================================================    
    '''

    def __init__(self):
        host = input("Enter a Host: ")
        ip = socket.gethostbyname(host)
        input(f'{host} has the IP of {ip}')


def main():
    try:
        program = Program()
        # program.find_ovpn_files(os.path.expanduser('~'))
        program.start()
        Netwatch()
    except KeyboardInterrupt:
        sleep(0.25)
        sys.exit()


if __name__ == "__main__":
    main()
