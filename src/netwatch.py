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

# Custom Imports
from modules import *
from logger import *
from themes import *


# Start Menu Classes
class Netwatch:
    """A menu class for Netwatch tools"""

    def __init__(self):
        self.program = Program()
        self.config_manager = ConfigManager()
        self.command_handler = CommandHandler()
        self.table_creator = TableCreator()
        self.logger = Logger()

        self.netwatch_prompt = self.config_manager.get(
            'general_config', 'prompt') + ' '
        self.tooldir = self.config_manager.get_path(
            'general_config', 'tooldir')
        self.scandir = self.config_manager.get_path(
            'general_config', 'scandir')
        # self.store_history = self.config_manager.getbool(
        #     'general_config', 'storehistory')

        self.run()

    def run(self) -> None:
        choice = input(self.netwatch_prompt).strip()
        choice = self.command_handler.autocomplete(choice)

        if choice:
            self.command_handler.execute(choice)

        match choice:
            case "0":
                print(AUTOATTACK_BANNER)
                AutoAttack()
            case "1":
                print(INFO_BANNER)
                InformationGathering()
            case _:
                self.__init__()


class AutoAttack:
    """A menu class for the Automated Attack Tool for HTB, TryHackMe, etc."""

    def __init__(self):
        self.program = Program()
        self.config_manager = ConfigManager()
        self.command_handler = CommandHandler()
        self.logger = Logger()
        self.table_creator = TableCreator()
        self.run()

    def run(self) -> None:
        self.program.clear_screen()
        updated_config_path = self.program.find_files(
            '.ovpn', os.path.expanduser('~'))
        # Run .ovpn file if found
        # Check for default value in config file
        if updated_config_path:
            self.start_ovpn(updated_config_path)

    def start_ovpn(self, updated_config_path: str) -> None:
        try:
            self.logger.info('Starting OpenVPN profile...')
            # print(os.getenv("TERM"))
            # subprocess.Popen(["gnome-terminal", "--", "sudo", "openvpn", updated_config_path])
            # subprocess.run(["sudo", "openvpn", updated_config_path])
        except subprocess.CalledProcessError as e:
            self.logger.error(f'An error occurred: {e}')
            print("\n")
            self.logger.info("Returning to previous context menu...")
            Netwatch()


class InformationGathering:
    """A menu class for Information Gathering tools"""

    def __init__(self):
        self.program = Program()
        self.config_manager = ConfigManager()
        self.command_handler = CommandHandler()
        self.logger = Logger()

        self.netwatch_prompt = self.config_manager.get(
            'general_config', 'prompt') + ' '

        self.run()

    def run(self) -> None:
        choice_info = input(self.netwatch_prompt).strip()
        choice_info = self.command_handler.autocomplete(choice_info)

        match choice_info:  # .strip()
            case "1":
                print(NMAP_BANNER)
                NmapMenu()
            case "2":
                print(PYDISCOVER_BANNER)
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
                [self.command_handler.execute(choice_info, choice) for choice in [
                    "Information_Gathering", "Core"]]
            case "clear" | "cls":
                self.command_handler.execute(choice_info)
            case "clean":
                self.command_handler.execute(choice_info)
            case "path" | "pwd":
                self.command_handler.execute(
                    choice_info, "Netwatch/Information_Gathering")
            case "exit" | "quit" | "end":
                self.command_handler.execute(choice_info)
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
        self.config_manager = ConfigManager()
        self.command_handler = CommandHandler()
        self.logger = Logger()
        self.nmap = Nmap()
        self.netwatch_prompt = "netwatch ~# "
        self.gitrepo = "https://github.com/nmap/nmap.git"
        self.target_prompt = "\nEnter target IP: "
        self.scan_file_name_prompt = "\nEnter scan file name: "
        self.target = None
        self.scan_path = None

        self.run()

    def run(self):
        if self.nmap.check_nmap():
            # try:
            self.target = input(self.target_prompt)
            self.scan_path = "nmap-" + "-" + \
                strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
            if os.path.isfile(self.scan_path):
                self.logger.info("File name already exists!")
                self.logger.info("Would you like to overwrite this file?")
                response = input("[y/n]: ")
                if response.lower() in ["y", "yes"]:
                    self.menu()
            else:
                self.program.clear_screen()
                self.menu()
        else:
            self.logger.error(
                "Nmap could not be installed. Returning to previous main menu...")
            Netwatch()

    def menu(self) -> None:
        print(NMAP_BANNER)
        self.logger.info(f'Scan Path -> {self.scan_path}')
        try:
            choice_nmap = input(self.netwatch_prompt)
            match choice_nmap:
                case "default" | "default scan" | "defaultscan":
                    self.nmap.scan(self.target, self.scan_path, "default_scan")
                    self.get_input()
                case "quick scan" | "quick" "quickscan":
                    self.nmap.scan(self.target, self.scan_path, "quick_scan")
                    self.get_input()
                case "intense scan" | "intense" | "intensescan":
                    self.nmap.scan(self.target, self.scan_path, "intense_scan")
                    self.get_input()
                case "vuln" | "vuln scan" | "vulnscan" | "vulnerability" | "vulnerability scan":
                    self.nmap.scan(self.target, self.scan_path, "vuln_scan")
                    self.get_input()
                case _ if choice_nmap.startswith("set "):
                    self.set_parameters(choice_nmap)
                case "?" | "help":
                    [self.command_handler.execute(choice_nmap, choice) for choice in [
                        "Nmap_Scans", "Nmap_Commands", "Core"]]
                case "clear" | "cls":
                    self.command_handler.execute(choice_nmap, "Nmap")
                case "clean":
                    self.command_handler.execute(choice_nmap, "Nmap")
                case "path" | "pwd":
                    self.command_handler.execute(
                        choice_nmap, "Netwatch/Information_Gathering/Nmap")
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
            self.logger.error(f"An error occurred: {e}\n")
            self.logger.info("Returning to main menu...")
            Netwatch()

    def get_input(self):
        response = self.nmap.prompt_input(
            "Would you like to run another scan? [y/n]: ")
        if response.lower() in ["y", "yes"]:
            self.run()
        else:
            self.logger.info("Returning to main menu...")
            Netwatch()

    # update scan file after using set target?
    def set_parameters(self, input: str) -> None:
        # _, param, value = input.split(" ", 2)
        parts = input.split(" ")
        if len(parts) < 3:
            self.logger.error("Invalid syntax! Usage: 'set <param> <value>'")
            return
            # self.menu(target, scan_path)
        _, param, value = parts
        if param == "target":
            self.target = value
        elif param == "log" or "scan":
            scan_name, _, self.scan_path = value.partition(" ")
            if not self.scan_path:
                self.scan_path = "nmap-" + scan_name + "-" + \
                    strftime("%Y-%m-%d_%H:%M", gmtime()) + ".log"
            self.scan_path = "nmap-" + scan_name + "-" + \
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
        self.sagemode.start(SAGEMODE_BANNER,
                            SAGEMODE_BANNER_TEXT, delay=0.001)


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
