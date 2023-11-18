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
#   Netwatch v2.0
#   by: @NCSickels

# Imports
import sys
import os
import configparser
import json
import socket
from time import gmtime, strftime, sleep
import argparse
import logging
import subprocess
from rich.console import Console
from rich.table import Table

# Common Functions


class Color:
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
    def __init__(self):
        self.config = configparser.ConfigParser()
        configFile = os.path.dirname(
            os.path.abspath(__file__)) + '/netwatch.cfg'
        self.config.read(configFile)
        self.installDir = os.path.dirname(os.path.abspath(__file__)) + '/'

    def get(self, section, option):
        return self.config.get(section, option)

    def getPath(self, section, option):
        return self.installDir + self.config.get(section, option)

    def getbool(self, section, option):
        return self.config.getboolean(section, option)


class Program:
    def __init__(self):
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator(self.configManager)
        self.configFile = os.path.dirname(
            os.path.abspath(__file__)) + '/netwatch.cfg'
        # self.original_stdout = sys.stdout
        # self.log_file = open('typescript.log', 'w')
        # sys.stdout = self.log_file

    def start(self) -> None:
        self.clearScr()
        self.createFolders()
        print(Netwatch.netwatchLogo)

    def createFolders(self) -> None:
        if not os.path.isdir(self.configManager.getPath("general_config", "toolDir")):
            os.makedirs(self.configManager.getPath(
                "general_config", "toolDir"))
        if not os.path.isdir(self.configManager.getPath("general_config", "logDir")):
            os.makedirs(self.configManager.getPath("general_config", "logDir"))

    def end(self) -> None:  # command_history: CommandHistory
        print("\n\nFinishing up...\n")
        sleep(0.25)
        sys.exit()

    def clean(self, path: str) -> None:
        # TODO: Update with new file check method
        print(
            f'\n{Color.WARNING}[!] Cleaning {path} directory...{Color.END}\n')
        if os.path.exists(path):
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            print(f'\t - Deleting {file_path} file...')
                        except Exception as e:
                            print(e)
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            os.rmdir(dir_path)
                            print(f'\t - Deleting {dir_path} directory...')
                        except Exception as e:
                            print(e)
                os.rmdir(path)
                print(
                    f'\n{Color.OKGREEN}[✔] {path} directory successfully cleaned.{Color.END}\n')
            else:
                raise FileNotFoundError(
                    f'{Color.RED}{path} directory not found!{Color.END}\n')
        else:
            raise FileNotFoundError(
                f'{Color.RED}Path {path} does not exist!{Color.END}\n')

    def printPath(self, module: str) -> None:
        split_module = module.split("/")
        if (len(split_module) <= 1):    # if module is in root directory (Netwatch/)
            print(
                f'\n{Color.OKBLUE}[*]{Color.END} Module: {split_module[0]}\n{Color.OKBLUE}[*]{Color.END} Path: {module+"/"}\n')
        else:
            print(
                f'\n{Color.OKBLUE}[*]{Color.END} Module -> {split_module[len(split_module)-1]}\n{Color.OKBLUE}[*]{Color.END} Path   -> {module+"/"}\n')

    def clearScr(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    # TODO: Implement 'cd' function

    def command(self, command: str, module=None) -> None:
        match command:
            case "update":
                # TODO: Add command history updates to each of these cases
                try:
                    subprocess.check_call(["../scripts/update.sh"], shell=True)
                except subprocess.CalledProcessError as e:
                    print(
                        f'{Color.RED}[-]{Color.END} Error occurred with update script: {e}')
            case "clear" | "cls":
                self.clearScr()
            case "clean":
                self.clean(self.configManager.getPath(
                    "general_config", "toolDir"))
                self.clean(self.configManager.getPath(
                    "general_config", "logDir"))
            case "help" | "?":
                self.tableCreator.displayTableFromFile(module)
                # self.tableCreator.displayTableFromFile("Core")

    def __del__(self):
        # sys.stdout = self.original_stdout
        # self.log_file.close()
        pass

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
            "Nmap": ["type", "options", "description"],
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
    netwatchLogo = '''
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
    v2.0.0                                     Noah Sickels (@NCSickels)     
===================================================================================\n
'''

    def __init__(self):
        self.configManager = ConfigManager()
        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '
        self.toolDir = self.configManager.getPath('general_config', 'toolDir')
        self.logDir = self.configManager.getPath('general_config', 'logDir')
        self.storeHistory = self.configManager.getbool(
            'general_config', 'storeHistory')

        self.commandHistory = CommandHistory()
        self.program = Program()  # Program(config, configFile)
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator(self.configManager)
        self.run()

    def run(self) -> None:
        choice = input(self.netwatchPrompt)
        self.commandHistory.update(choice)
        match choice:
            case "1":
                print(InformationGathering.menuLogo)
                InformationGathering()
            case "?" | "help":
                self.program.command(choice, "Main")
                self.program.command(choice, "Core")
                # self.commandHistory.update(choice)
            case "update":
                self.program.command(choice, "Netwatch")
            case "\r" | "\n" | "" | " " | "back":
                pass
            case "history":
                pass
                # self.commandHistory.print()
            case "history -c" | "history --clear":
                pass
                # self.commandHistory.clear()
            case "clear" | "cls":
                self.program.command(choice)
            case "clean":
                self.program.command(choice)
            case "path" | "pwd":
                # Print path using Program.command instead?
                self.program.printPath("netwatch")
            case "exit" | "quit" | "end":
                self.program.end()
                # self.program.end(self.commandHistory.save())
            case _:
                print(
                    f'{Color.RED}[-]{Color.END} Unknown input: {choice}. Type "?" for help.')
                self.__init__()
        self.__init__()

    def completed(self) -> None:
        input("\nClick [return] to continue...")
        self.__init__()


class InformationGathering:
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
                print(PortScanner.portScannerLogo)
                pass
                # Currently not working
                # PortScanner()
            case "3":
                print(Host2IP.host2ipLogo)
                Host2IP()
            case "4":  # Sagemode
                pass
            case "?" | "help":
                self.program.command(choiceInfo, "Information_Gathering")
                self.program.command(choiceInfo, "Core")
            case "clear" | "cls":
                self.program.command(choiceInfo)
            case "clean":
                self.program.command(choiceInfo)
                self.completed()
            case "path" | "pwd":
                self.program.printPath("Netwatch/Information_Gathering")
            case "exit" | "quit" | "end":
                self.program.end()
            case "back":
                print((f'\nReturning to {Color.OKBLUE}Netwatch'
                       f'{Color.END} menu...\n'))
                Netwatch()
            case _:
                print(
                    f'{Color.RED}[-]{Color.END} Unknown input: {choiceInfo}. Type "?" for help.')
                self.__init__()
        self.__init__()

    def completed(self) -> None:
        input("\nClick [return] to continue...")
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
        self.configManager = ConfigManager()
        self.program = Program()
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
            logName = input(self.logFileNamePrompt)
            logPath = "nmap-" + logName + "-" + \
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
        print(f'\n{Color.OKBLUE}[*]{Color.END} Target(s) -> {target}')
        print(f'{Color.OKBLUE}[*]{Color.END} Log Path  -> {logPath}\n')
        try:
            choiceNmap = input(self.netwatchPrompt)
            match choiceNmap:
                case "quick scan" | "quick" "quickscan":
                    os.system(f'\nnmap -T4 -F -v -oN {logPath} {target}')  # \n
                    print((f'\n{Color.OKGREEN}[✔] Scan completed, log saved to:'
                           f'{Color.END} {logPath}'))
                    self.promptForAnotherScan(target, logPath)
                case "intense scan" | "intense" | "intensescan":
                    os.system(f'\nnmap -T4 -A -v -oN {logPath} {target}')  # \n
                    print((f'\n{Color.OKGREEN}[✔] Scan completed, log saved to:'
                           f'{Color.END} {logPath}'))
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
                    self.program.command(choiceNmap, "Nmap")
                    self.program.command(choiceNmap, "Core")
                case "clear" | "cls":
                    self.program.command(choiceNmap, "Nmap")
                case "clean":
                    self.program.command(choiceNmap, "Nmap")
                case "path" | "pwd":
                    self.program.printPath(
                        "Netwatch/Information_Gathering/Nmap")
                    self.menu(target, logPath)
                case "exit" | "quit" | "end":
                    self.program.end()
                case "back":
                    print((f'\nReturning to {Color.OKBLUE}Information Gathering'
                           f'{Color.END} menu...\n'))
                    InformationGathering()
                case _:
                    print(
                        f'{Color.RED}[-]{Color.END} Unknown input: {choiceNmap}. Type "?" for help.')
                    self.menu(target, logPath)
            self.menu(target, logPath)
        except KeyboardInterrupt:
            print("\n")
            InformationGathering()

    def promptForAnotherScan(self, target: int, logPath: str) -> None:
        response = input(
            "\nWould you like to run another scan? [y/n]: ").lower()
        if response in ["y", "yes"]:
            self.menu(target, logPath)
        else:
            print((f'\nReturning to {Color.OKBLUE}Netwatch'
                   f'{Color.END} menu...\n'))
            Netwatch()

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
        program.start()
        commandHistory = CommandHistory()
        Netwatch()
    except KeyboardInterrupt:
        print("Finishing up...\n")
        sleep(0.25)
        sys.exit()


if __name__ == "__main__":
    main()
