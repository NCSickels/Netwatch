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
            'netwatch', 'storeHistory')
        self.logDir = self.configManager.getPath('netwatch', 'logDir')
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

    def start(self) -> None:
        self.clearScr()
        self.createFolders()
        print(Netwatch.netwatchLogo)

    def createFolders(self) -> None:
        if not os.path.isdir(self.configManager.getPath("netwatch", "toolDir")):
            os.makedirs(self.configManager.getPath("netwatch", "toolDir"))
        if not os.path.isdir(self.configManager.getPath("netwatch", "logDir")):
            os.makedirs(self.configManager.getPath("netwatch", "logDir"))

    def end(self) -> None:  # command_history: CommandHistory
        print("Finishing up...\n")
        # with open(self.configFile, 'w') as configfile:
        #    self.config.write(configfile)
        # command_history.save()
        sleep(0.25)
        sys.exit()

    def clean(self, path: str) -> None:
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

    def command(self, command: str) -> None:
        match command:
            case "update":
                # TODO: Add command history updates to each of these cases
                os.system(
                    "git clone --depth=1 https://github.com/NCSickels/netwatch.git")
                os.system("cd netwatch && chmod +x update.sh && ./update.sh")
                os.system("netwatch")
            case "clear" | "cls":
                self.clearScr()
            case "clean":
                self.clean(self.configManager.getPath("netwatch", "toolDir"))
                self.clean(self.configManager.getPath("netwatch", "logDir"))
            case "help" | "?":
                self.tableCreator.displayTableFromFile()


class TableCreator:
    def __init__(self, configManager):
        self.console = Console()
        self.jsonFile = os.path.dirname(os.path.abspath(
            __file__)) + '/' + configManager.get('netwatch', 'mainMenuDataPath')

    @staticmethod
    def readJson(file_path: str) -> dict:
        with open(file_path) as json_file:
            data = json.load(json_file)
            return data

    def createTable(self, header_data: dict, column_data: list, row_data: list) -> None:
        table = Table(
            show_header=header_data.get("show_header", True),
            header_style=header_data.get("header_style", "bold white"),
            title=header_data.get("title", ""),
            width=int(header_data.get("width", 84)),
            show_lines=True)
        for column in column_data:
            table.add_column(
                column.get("title", ""),
                style=column.get("style", ""),
                justify=column.get("justify", "right"),
                width=column.get("width", 30))
        column_names = [column.get("title", "").lower()
                        for column in column_data]
        for row in row_data:
            row_values = [str(row.get(column_name, ""))
                          for column_name in column_names]
            table.add_row(*row_values)
        return table

    def displayTable(self, jsonData: dict) -> None:
        for tableName, tableData in jsonData.items():
            header_data = tableData[0]['header'][0]
            column_data = tableData[0]['columns']
            row_data = tableData[0]['rows']
            table = self.createTable(header_data, column_data, row_data)
            self.console.print(table)
            print("\n")

    def displayTableFromFile(self) -> None:
        jsonData = self.readJson(self.jsonFile)
        self.displayTable(jsonData)


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
            'netwatch', 'prompt') + ' '
        self.toolDir = self.configManager.getPath('netwatch', 'toolDir')
        self.logDir = self.configManager.getPath('netwatch', 'logDir')
        self.storeHistory = self.configManager.getbool(
            'netwatch', 'storeHistory')

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
                self.program.command(choice)
                # self.commandHistory.update(choice)
                # self.tableCreator.displayTableFromFile()
                self.__init__()
            case "update":
                self.program.command(choice)
                # self.__init__()
                # self.update()
                self.__init__()
            case "\r" | "\n" | "" | " " | "back":
                self.__init__()
            case "history":
                # self.commandHistory.print()
                self.__init__()
            case "history -c" | "history --clear":
                # self.commandHistory.clear()
                self.__init__()
            case "clear" | "cls":
                self.program.command(choice)
                # self.program.clearScr()
                self.__init__()
            case "clean":
                self.program.command(choice)
                # self.program.clean(self.toolDir)
                # self.program.clean(self.logDir)
                self.__init__()
            case "path" | "pwd":
                self.program.printPath("netwatch")
                self.__init__()
            case "exit" | "quit" | "end":
                self.program.end()
                # self.program.end(self.commandHistory.save())
            case _:
                print(
                    f'{Color.RED}[-]{Color.END} Unknown input: {choice}. Type "?" for help.')
                self.__init__()
        self.completed()

    def completed(self) -> None:
        input("\nClick [return] to continue...")
        self.__init__()

    # # TODO: Check me!
    # def update(self) -> None:
    #     os.system("git clone --depth=1 https://github.com/NCSickels/netwatch.git")
    #     os.system("cd netwatch && chmod +x update.sh && ./update.sh")
    #     os.system("netwatch")


class InformationGathering:
    menuLogo = '''
===================================================================================
                            88 88b 88 888888  dP"Yb
                            88 88Yb88 88__   dP   Yb
                            88 88 Y88 88""   Yb   dP
                            88 88  Y8 88      YbodP
===================================================================================
    '''

    def __init__(self):
        self.configManager = ConfigManager()
        self.netwatchPrompt = self.configManager.get(
            'netwatch', 'prompt') + ' '

        self.run()

    def run(self) -> None:
        choiceInfo = input(self.netwatchPrompt)
        match choiceInfo:
            case "1":
                print(Nmap.nmapLogo)
                Nmap()
                pass
            case "2":
                print(PortScanner.portScannerLogo)
                PortScanner()
            case "3":
                print(Host2IP.host2ipLogo)
                Host2IP()
            case "?" | "help":
                pass
            case "clear" | "cls":
                pass
            case "clean":
                pass
            case "path" | "pwd":
                pass
            case "exit" | "quit" | "end":
                pass
            case "back":
                Netwatch()
            case _:
                print(
                    f'{Color.RED}[-]{Color.END} Unknown input: {choiceInfo}. Type "?" for help.')
                self.__init__()
        self.completed()

    def completed(self) -> None:
        input("\nClick [return] to continue...")
        self.__init__()


class Nmap:
    nmapLogo = '''
===================================================================================
                            88b 88 8b    d8    db    88""Yb
                            88Yb88 88b  d88   dPYb   88__dP
                            88 Y88 88YbdP88  dP__Yb  88"""
                            88  Y8 88 YY 88 dP""""Yb 88
===================================================================================
'''

    def __init__(self):
        self.configManager = ConfigManager()
        self.program = Program()
        self.netwatchPrompt = self.configManager.get(
            'netwatch', 'prompt') + ' '
        self.nmapDir = self.configManager.getPath('nmap', 'nmapdir')
        self.gitRepo = self.configManager.get('nmap', 'gitrepository')
        # self.log = self.configManager.getPath('nmap', 'logPath')
        self.targetPrompt = "Enter target IP: "
        self.logFileNamePrompt = "Enter log file name: "

        if not self.installed():
            self.install()
            self.run()
        else:
            self.run()

    def installed(self) -> bool:
        return ((os.path.isfile("/usr/bin/nmap") or os.path.isfile("/usr/local/bin/nmap")))

    def install(self) -> None:
        print(
            f'\n{Color.WARNING}[!] Installing Nmap...{Color.END}\n')

        exitStatus = os.system("sudo apt-get install nmap")
        if exitStatus == 0:
            print(
                f'\n{Color.OKGREEN}[✔] Nmap successfully installed.{Color.END}\n')
        else:
            print(
                f'\n{Color.RED}[-]{Color.END} Error installing Nmap.\n')

    def run(self) -> None:
        try:
            target = input(self.targetPrompt)
            logName = input(self.logFileNamePrompt)
            logPath = "nmap-" + logName + "-" + \
                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
            # logPath = self.nmapDir + input(self.logFileNamePrompt)
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
        self.program.clearScr()
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
                    response = input(
                        "\nWould you like to run another scan? [y/n]: ").lower()
                    if response == "y" or response == "yes":
                        self.menu(target, logPath)
                    else:
                        print((f'\nReturning to {Color.OKBLUE}Netwatch'
                              f'{Color.END} menu...\n'))
                        Netwatch()
                        # InformationGathering()
                case "intense scan" | "intense" | "intensescan":
                    os.system(f'\nnmap -T4 -A -v -oN {logPath} {target}')  # \n
                    print((f'\n{Color.OKGREEN}[✔] Scan completed, log saved to:'
                           f'{Color.END} {logPath}'))
                    response = input(
                        "\nWould you like to run another scan? [y/n]: ").lower()
                    if response == "y" or response == "yes":
                        self.menu(target, logPath)
                    else:
                        print((f'\nReturning to {Color.OKBLUE}Netwatch'
                              f'{Color.END} menu...\n'))
                        Netwatch()
                        # InformationGathering()
                case "?" | "help":
                    self.program.command(choiceNmap)
                    # self.commandHistory.update(choiceNmap)
                    # self.tableCreator.displayTableFromFile()
                    self.menu(target, logPath)
                case "clear" | "cls":
                    self.program.command(choiceNmap)
                    # self.program.clearScr()
                    self.menu(target, logPath)
                case "clean":
                    self.program.command(choiceNmap)
                    # self.program.clean(self.nmapDir)
                    self.menu(target, logPath)
                case "path" | "pwd":
                    self.program.printPath(
                        "Netwatch/Information_Gathering/Nmap")
                case "exit" | "quit" | "end":
                    self.program.end()
                case "back":
                    InformationGathering()
                case _:
                    self.menu(target, logPath)
        except KeyboardInterrupt:
            InformationGathering()


class PortScanner:
    portScannerLogo = '''\n
===================================================================================
        d8888b.  .d88b.  d8888b. d888888b .d8888.  .o88b.  .d8b.  d8b   db 
        88  `8D .8P  Y8. 88  `8D `~~88~~' 88'  YP d8P  Y8 d8' `8b 888o  88 
        88oodD' 88    88 88oobY'    88    `8bo.   8P      88ooo88 88V8o 88 
        88~~~   88    88 88`8b      88      `Y8b. 8b      88~~~88 88 V8o88 
        88      `8b  d8' 88 `88.    88    db   8D Y8b  d8 88   88 88  V888 
        88       `Y88P'  88   YD    YP    `8888Y'  `Y88P' YP   YP VP   V8P 
===================================================================================
    '''

    def __init__(self) -> None:
        self.targetPrompt = "Enter target IP(s): "
        self.portPrompt = "Enter port(s) to scan: "
        self.logNamePrompt = "Enter log file name: "

    def run(self) -> None:
        target = input(self.targetPrompt)
        port = input(self.portPrompt)
        logName = input(self.logNamePrompt)
        logPath = "portScan-" + logName + "-" + \
            strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"

    def scan(self) -> None:
        pass


class Host2IP:

    host2ipLogo = '''\n
===================================================================================
                    88  88  dP"Yb  .dP"Y8 888888 oP"Yb. 88 88""Yb
                    88  88 dP   Yb `Ybo."   88   "' dP' 88 88__dP
                    888888 Yb   dP o.`Y8b   88     dP'  88 88"""
                    88  88  YbodP  8bodP'   88   .d8888 88 88
===================================================================================    
    '''

    def __init__(self):
        # utilities.clearScr()
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
        Program.end()


if __name__ == "__main__":
    main()
