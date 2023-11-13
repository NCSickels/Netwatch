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
import time
# from time import gmtime, strftime, sleep
import json
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


class Utilities:
    command_history = set()

    def __init__(self):
        pass

    def clearScr() -> None:
        if (os.name == 'posix'):
            os.system('clear')
        else:
            os.system('cls')

    def commandHistoryUpdate(command: str) -> None:
        Utilities.command_history.add(command)

    def commandHistoryPrint() -> None:
        print("\n")
        i = 0
        for command in Utilities.command_history:
            print(f"{i}: {command}")
            i += 1
        print("\n")

    def commandHistoryClear() -> None:
        Utilities.command_history.clear()
        print(f'\n{Color.OKGREEN}[✔] Command history cleared.{Color.END}\n')

    def commandHistorySave() -> None:
        i = 0
        with open(logDir + "/command_history-" + time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime()), 'a') as history_log:
            for command in Utilities.command_history:
                history_log.write(f"{i}: {command}\n")

    def endProgram() -> None:
        print("Finishing up...\n")
        with open(configFile, 'w') as configfile:
            config.write(configfile)
        # TODO: Add terminal output save to log file here
        Utilities.commandHistorySave()
        time.sleep(0.25)
        sys.exit()

    def clean(path: str) -> None:
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

    def printPath(module: str) -> None:
        split_module = module.split("/")
        if (len(split_module) <= 1):    # if module is in root directory (Fsoceity/)
            print(
                f'\n{Color.OKBLUE}[*]{Color.END} Module: {split_module[0]}\n{Color.OKBLUE}[*]{Color.END} Path: {module+"/"}\n')
        else:
            print(
                f'\n{Color.OKBLUE}[*]{Color.END} Module -> {split_module[len(split_module)-1]}\n{Color.OKBLUE}[*]{Color.END} Path   -> {module+"/"}\n')

    def readJson(file_path: str) -> None:
        with open(file_path, 'r') as json_file:
            return json.load(json_file)
            # jsonData = json.load(json_file)

    def createTable(header_data: dict, column_data: list, row_data: list) -> None:
        console = Console()
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

    def helpMenu() -> None:
        print("\n")
        console = Console()
        for tableName, tableData in jsonData.items():  # tableName, tableData
            header_data = tableData[0]['header'][0]
            column_data = tableData[0]['columns']
            row_data = tableData[0]['rows']
            table = Utilities.createTable(header_data, column_data, row_data)
            console.print(table)
            print("\n")


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
        self.createFolders()
        choice = input(netwatchPrompt)
        Utilities.commandHistoryUpdate(choice)
        match choice:
            case "1":
                print(InformationGathering.menuLogo)
                InformationGathering()
            case "?" | "help":
                Utilities.helpMenu()
                self.__init__()
            case "update":
                self.update()
            case "\r" | "\n" | "" | " " | "back":
                self.__init__()
            case "history":
                Utilities.commandHistoryPrint()
                self.__init__()
            case "history -c" | "history --clear":
                Utilities.commandHistoryClear()
                self.__init__()
            case "clear" | "cls":
                Utilities.clearScr()
                self.__init__()
            case "clean":
                Utilities.clean(logDir)
                Utilities.clean(toolDir)
                self.__init__()
            case "path" | "pwd":
                Utilities.printPath("Netwatch")
                self.__init__()
            case "exit" | "quit" | "end":
                Utilities.endProgram()
            case _:
                print(
                    f'{Color.RED}[-]{Color.END} Unknown input: {choice}. Type "?" for help.')
                self.__init__()
        self.completed()

    def createFolders(self) -> None:
        if not os.path.isdir(toolDir):
            os.makedirs(toolDir)
        if not os.path.isdir(logDir):
            os.makedirs(logDir)

    def completed(self) -> None:
        input("\nClick [return] to continue...")
        self.__init__()

    def update(self) -> None:
        os.system("git clone --depth=1 https://github.com/NCSickels/netwatch.git")
        os.system("cd netwatch && chmod +x update.sh && ./update.sh")
        os.system("netwatch")


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
        choiceInfo = input(netwatchPrompt)
        match choiceInfo:
            case "1":
                pass  # Nmap
            case "2":
                pass  # Port Scanner
            case "3":
                pass  # Host2IP
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


if __name__ == "__main__":
    try:
        installDir = os.path.dirname(os.path.abspath(__file__)) + '/'
        configFile = installDir + "/netwatch.cfg"
        print(installDir)
        config = configparser.RawConfigParser()
        config.read(configFile)
        toolDir = installDir + config.get('netwatch', 'toolDir')
        logDir = installDir + config.get('netwatch', 'logDir')
        storeHistory = config.get('netwatch', 'storeHistory')

        file_path = installDir + "/mainHelpMenuData.json"
        # if not os.path.exists(file_path):
        #     print("Error here!")

        jsonData = Utilities.readJson(file_path)
        # randomColor = [Color.HEADER, Color.IMPORTANT, Color.NOTICE, Color.BLUE, Color.OKBLUE,
        #            Color.OKGREEN, Color.WARNING, Color.RED, Color.END, Color.UNDERLINE, Color.BOLD, Color.LOGGING]
        # random.shuffle(randomColor)

        Utilities.clearScr()

        netwatchPrompt = "netwatch ~# "
        print(Netwatch.netwatchLogo)
        Netwatch()
    except KeyboardInterrupt:
        Utilities.endProgram()
