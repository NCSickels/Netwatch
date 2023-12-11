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
#   Netwatch v3.1.0
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

# Custom Imports
from modules import constants
from modules.tablecreator import TableCreator
from modules.termutils import Color, Notify, NotifyDataParser, NotifyNmap, NotifySagemode
from modules.sites import sites, soft404_indicators, user_agents

# Utility Classes


class Program:
    "A class for main program functions"

    def __init__(self):
        self.updateHandler = UpdateHandler()
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator()
        self.notify = Notify()
        self.configFile = os.path.dirname(
            os.path.abspath(__file__)) + '/netwatch.cfg'

    def start(self) -> None:
        self.clearScreen()
        print(Netwatch.netwatchLogo)
        self.updateHandler.checkForUpdate()
        self.createFolders([("general_config", "tooldir"),
                            ("general_config", "logdir"),
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
        self.notify.findFiles(file_type)  # (".ovpn")
        try:
            search_path = os.path.join(directory, '**/*'+file_type)
            files = glob.glob(search_path, recursive=True)
            if not files:
                self.notify.noFilesFound(file_type)  # (".ovpn")
                return
            for filename in files:
                self.notify.foundFiles(filename)
                response = input("Use this file? [y/n]: ").lower()
                if response in ["y", "yes"]:
                    self.configManager.set(
                        "general_config", "ovpn_path", filename)
                    self.notify.setFiles(filename)
                    return filename
            self.notify.noFilesFound(file_type, " other")
        except Exception as e:
            self.notify.exception(e)
            self.notify.noFilesFound(file_type)

    def __del__(self):
        # sys.stdout = self.original_stdout
        # self.log_file.close()
        pass


class UpdateHandler:
    "A class for handling updates for the Netwatch tool"

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

    def is_newer_version(self, remote_version: str, local_version: str) -> bool:
        remote_version_revisions = list(map(int, remote_version.split('.')))
        local_version_revisions = list(map(int, local_version.split('.')))
        return remote_version_revisions > local_version_revisions

    def update(self) -> None:
        repo_dir = os.path.dirname(os.path.realpath(__file__))
        # ensure we're performing git command in the local git repo directory
        os.chdir(repo_dir)
        subprocess.run(["git", "pull"])


class ConfigManager:
    "A class for managing configuration files"

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.notify = Notify()
        self.configFile = os.path.dirname(
            os.path.abspath(__file__)) + '/netwatch.cfg'
        self.config.read(self.configFile)
        self.installDir = os.path.dirname(os.path.abspath(__file__)) + '/'

    def get(self, section: any, option: any) -> str:
        return self.config.get(section, option)

    def set(self, section: any, key: any, value: any) -> None:
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, key, value)
            with open(self.configFile, 'w') as f:
                self.config.write(f)
        except Exception as e:
            self.notify.exception(e)

    def getPath(self, section: any, option: any) -> str:
        return self.installDir + self.config.get(section, option)

    def getbool(self, section: str, option: str) -> bool:
        return self.config.getboolean(section, option)


class ProgramInstallationManager:
    "A class for managing program installations for various tools used in Netwatch"

    def __init__(self, program_name):
        self.program_name = program_name
        self.notify = Notify()

    def installed(self) -> bool:
        try:
            subprocess.check_output(["which", self.program_name])
            return True
        except subprocess.CalledProcessError:
            return False

    def install(self) -> bool:
        try:
            subprocess.check_call(
                ["sudo", "apt", "install", "-y", self.program_name])
            return True
        except subprocess.CalledProcessError as e:
            self.notify.installError(self.program_name)
            self.notify.exception(e)
            return False

    def checkAndInstall(self) -> bool:
        if not self.installed():
            self.notify.programNotInstalled(self.program_name)
            return self.install()
        else:
            self.notify.programAlreadyInstalled(self.program_name)
            return True


class CommandHandler:
    "A class for handling commands from the user"

    def __init__(self):
        self.program = Program()
        self.updateHandler = UpdateHandler()
        self.configManager = ConfigManager()
        self.tableCreator = TableCreator()
        self.notify = Notify()

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
                    "general_config", "toolDir"))
                self.program.clean(self.configManager.getPath(
                    "general_config", "logDir"))
                self.program.clean(
                    self.configManager.getPath("sagemode", "datadir"))
                # self.completed()
            case "path" | "pwd":
                self.program.printPath(module)
            case "exit" | "quit" | "end":
                self.program.end()

    def completed(self) -> None:
        input("\nClick [return] to continue...")


class CommandHistory:
    "A class for managing command history"

    def __init__(self):
        self.configManager = ConfigManager()
        self.storeHistory = self.configManager.getbool(
            'general_config', 'storehistory')
        self.logDir = self.configManager.getPath('general_config', 'logdir')
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
        self.program = Program()  # Program(config, configFile)
        self.configManager = ConfigManager()
        self.commandHandler = CommandHandler()
        self.notify = Notify()
        self.tableCreator = TableCreator()

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '
        self.toolDir = self.configManager.getPath('general_config', 'tooldir')
        self.logDir = self.configManager.getPath('general_config', 'logdir')
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
            self.notify.runOvpn(os.path.basename(updatedConfigPath))
            # print(os.getenv("TERM"))
            # subprocess.Popen(["gnome-terminal", "--", "sudo", "openvpn", updatedConfigPath])
            # subprocess.run(["sudo", "openvpn", updatedConfigPath])
        except subprocess.CalledProcessError as e:
            self.notify.exception(e)
            print("\n")
            self.notify.previousContextMenu("Netwatch")
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

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '

        self.run()

    def run(self) -> None:
        choiceInfo = input(self.netwatchPrompt)
        match choiceInfo:  # .strip()
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
        self.notify = Notify()

        self.netwatchPrompt = self.configManager.get(
            'general_config', 'prompt') + ' '
        self.gitRepo = self.configManager.get('nmap', 'gitrepository')
        self.targetPrompt = "\nEnter target IP: "
        self.logFileNamePrompt = "\nEnter log file name: "

        self.checkInstall()

    def checkInstall(self) -> None:
        checkNmap = ProgramInstallationManager("nmap")
        programIsInstalled = checkNmap.checkAndInstall()
        if programIsInstalled:
            self.run()
        else:
            self.notify.previousContextMenu("Information Gathering")
            InformationGathering()

    def run(self) -> None:
        try:
            target = input(self.targetPrompt)
            logPath = "nmap-" + "-" + \
                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
            if os.path.isfile(logPath):
                self.notify.logFileConflict()
                self.notify.overwriteLogFile()
                response = input("[y/n]: ")
                if response.lower() == "y" or response.lower() == "yes":
                    self.menu(target, logPath)
                else:
                    self.run()
            self.menu(target, logPath)
        except KeyboardInterrupt:
            print("\n")
            self.notify.previousContextMenu("Information Gathering")
            InformationGathering()

    def menu(self, target: int, logPath: str) -> None:
        print(self.nmapLogo)
        self.notify.currentTarget(target)
        self.notify.currentLogPath(logPath)
        try:
            choiceNmap = input(self.netwatchPrompt)
            match choiceNmap:  # .strip()
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
            self.notify.previousContextMenu("Information Gathering")
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
        self.notify.promptForAnotherScan()
        response = input("[y/n]: ")
        if response.lower() in ["y", "yes"]:
            self.menu(target, logPath)
        else:
            self.notify.previousContextMenu("Netwatch")
            Netwatch()


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


class PortScanner:
    "A custom port scanner"

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
            self.notify.previousContextMenu("Information Gathering")
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
            self.notify.previousContextMenu("Information Gathering")
            InformationGathering()

    def ip2Int(self, ip: str) -> int:
        octets = ip.split('.')
        return ((int(octets[0]) << 24) + (int(octets[1]) << 16) +
                (int(octets[2]) << 8) + int(octets[3]))


class Host2IP:
    "A class for converting a hostname to an IP address"

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
        Netwatch()
    except KeyboardInterrupt:
        sleep(0.25)
        sys.exit()


if __name__ == "__main__":
    main()
