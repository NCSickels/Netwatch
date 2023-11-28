import os
import re
import sys
import ipaddress
import time
import tabulate

from IPy import IP
from rich.console import Console
from rich import print as rprint
from colorama import Fore, Style

from modules.sites import sites, soft404_indicators, user_agents
from config import parsersettings as settings
from modules import constants


class ColorConfig:
    def __init__(self):
        self.console = Console()

    # Source: https://github.com/django/django/blob/master/django/core/management/color.py
    def supportsColor():
        """
        Returns True if the running system's terminal supports color, and False otherwise.
        """
        platform = sys.platform
        supported_platform = platform != "Pocket PC" and (
            platform != "win32" or "ANSICON" in os.environ)

        # isatty is not always implemented, #6223.
        is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
        return supported_platform and is_a_tty


class LamePrint:
    def __init__(self):
        pass

    # Color output green (successprint)
    def sprint(self, *args, **kwargs) -> None:
        self.coloredPrint("\033[1;32m", args, kwargs)

    def eprint(self, *args, **kwargs) -> None:
        self.coloredPrint("\033[1;31m", args, kwargs)

    # Print text with specified color code
    def coloredPrint(self, color, args, kwargs) -> None:
        if (not settings.colorSupported):
            print(args, kwargs)
            return

        coloredArgs = []
        for arg in args:
            if arg == None or not isinstance(arg, str):
                coloredArgs.append('')
                continue
            coloredArgs.append(color + arg + "\033[1;m")
        print(*coloredArgs, file=sys.stderr, **kwargs)

    # Print only if raw option hasnt been set
    def hprint(*args, **kwargs) -> None:
        settings.printHumanFriendlyText
        if (settings.printHumanFriendlyText):
            print(*args, **kwargs)

    def getHeader(self, text: str) -> None:
        return f"\n{text}\n{'-' * len(text)}\n"

    def header(self, text: str) -> None:
        print(self.getHeader(text))


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


class Notify:
    "A helper class for notifications of Netwatch process"

    def __init__(self):
        self.console = Console()

    # General Use Methods
    def update(self, remoteVersion: str, localVersion: str) -> None:
        self.console.print(
            f"[red][[bright_red]![red]] [yellow]Update Available!\n[/yellow]"
            + f"[red][[yellow]![red]] [bright_yellow]You are running Version: [bright_green]{localVersion}\n"
            + f"[red][[/red][yellow]![red]][bright_yellow] New Version Available: [bright_green]{remoteVersion}")

    def upToDate(self) -> None:
        self.console.print(
            f"\n[red][[yellow]![red]] [bright_yellow]Netwatch is up to date.\n")

    def endProgram(self) -> None:
        self.console.print(
            f"\n[red][[yellow]![red]] [bright_yellow]Finishing up...\n")

    def previousContextMenu(self, module: str) -> None:
        self.console.print((f"\n[bright_yellow]Returning to "
                            f"[bright_blue]{module} [bright_yellow]menu...\n"))

    def unknownInput(self, choice: str) -> None:
        self.console.print(
            f"[bright_red][[bright_red]![bright_red]] [bright_yellow]Unknown input: [bright_red]{choice}. [bright_yellow]Type [bright_red]'?' [bright_yellow]for help.")

    def programNotInstalled(self, program: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Program: [bright_blue]{program} [bright_yellow]not found. Attempting to install...\n")

    def programAlreadyInstalled(self, program: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Program: [bright_blue]{program} [bright_yellow]already installed. Skipping installation...\n")

    def completed(self) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Operation completed.\n")

    # File Operations Methods
    def findFiles(self, file_type: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Searching for [bright_blue]{file_type} [bright_yellow]files...")

    def foundFiles(self, file: str, file_type: str) -> None:
        self.console.print((f"\n[red][[yellow]![red]] [bright_yellow]Found [bright_blue]"
                            f"{file_type} [bright_yellow]file: [bright_red]{file}\n"))

    def noFilesFound(self, file_type: str, modifier="") -> None:
        self.console.print((f"\n[red][[bright_red]![red]] [yellow]No{modifier}"
                            f"[bright_blue]{file_type} [bright_yellow]files found. Please add the path to the [red].cfg [bright_yellow]file manually.\n"))

    def setFiles(self, file: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Selected file: [bright_red]{file}\n")

    def cleaningDirectory(self, path: str) -> None:
        self.console.print(
            f"\n[red][[yellow]![red]] [bright_yellow]Cleaning [bright_blue]~/Netwatch/src/{os.path.basename(os.path.normpath(path))}/ [bright_yellow]directory...")

    def deletingFile(self, file: str) -> None:
        self.console.print(
            f"\n\t[red][[yellow]-[red]] [bright_yellow]Deleting file: [bright_blue]{os.path.basename(file)}[bright_yellow]")

    def directoryCleaned(self, path: str, files_found=False) -> None:
        if files_found:
            self.console.print(
                f"\n[black][[green]*[black]] [bright_yellow]Directory: [bright_blue]~/Netwatch/src/{os.path.basename(os.path.normpath(path))}/ [bright_yellow]successfully cleaned.\n")
        else:
            self.console.print(
                f"\n[black][[green]*[black]] [bright_yellow]No files found in [bright_blue]~/Netwatch/src/{os.path.basename(os.path.normpath(path))}/ [bright_yellow]directory.\n")

    def currentDirPath(self, module: any, path=None) -> None:
        split_module = module.split("/")
        if (len(split_module) <= 1):    # if module is in root directory (Netwatch/)
            self.console.print(
                f"\n[black][[red]*[black]] [bright_yellow]Module [bright_black]-> [bright_red]{split_module[0]}\n[black][[red]*[black]] [bright_yellow]Path [bright_black]  -> [bright_red]{module+'/'}\n")
        else:
            self.console.print(
                f"\n[black][[red]*[black]] [bright_yellow]Module [bright_black]-> [bright_red]{split_module[len(split_module)-1]}\n[black][[red]*[black]] [bright_yellow]Path [bright_black]  -> [bright_red]{module+'/'}\n")

    # Error Handling Methods
    def exception(self, error: str) -> None:
        self.console.print(
            f"[black][[red]![black]] [bright_yellow]An error occurred: [bright_red]{error}...")

    def installError(self, program: str) -> None:
        self.console.print(
            f"[bright_red][[bright_red]![bright_red]] [bright_yellow]An error installing: [bright_blue]{program}[bright_yellow]!\n")

    def updateScriptError(self, error: str) -> None:
        self.console.print(
            f"[bright_red][[bright_red]![bright_red]] [bright_yellow]A problem occured while updating: [bright_red]{error}")

    # Methods for AutoAttack Tool
    def runOvpn(self, ovpnPath: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Starting OpenVPN profile: [bright_blue]{ovpnPath}\n")

    # Methods for InformationGathering
    # Methods for Nmap
    def logFileConflict(self) -> None:
        self.console.print(
            f"\n[bright_red][[bright_red]![bright_red]] [bright_yellow]Log file already exists!")

    def overwriteLogFile(self) -> None:
        self.console.print(
            f"\n[red][[yellow]![red]] [bright_yellow]Would you like to overwrite the log file?")

    def currentTarget(self, target: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Target [bright_black]-> [bright_red]{target}")

    def currentLogPath(self, logPath: str) -> None:
        self.console.print(
            f"[black][[red]*[black]] [bright_yellow]Log Path [bright_black]-> [bright_red]{logPath}\n")

    def scanCompleted(self, logPath: str) -> None:
        self.console.print(
            # ✔
            f"\n[black][[red]*[black]] [orange3]Scan completed, log saved to: [bright_blue]{logPath}")

    def promptForAnotherScan(self) -> None:
        self.console.print(
            f"\n[red][[yellow]![red]] [bright_yellow]Would you like to run another scan?")


class NotifyNmap:
    "A helper class for notifications of the Nmap and Data Parser modules"

    def __init__(self):
        self.console = Console()

    def attemptingToOpenFile(self, file: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Attempting to open: [bright_blue]{file}")

    def filePreviouslyImported(self, file: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Skipping previously imported file: [bright_blue]{file}")

    def loadingFileCount(self, count: int, total: int, file: str) -> None:
        self.console.print(
            f"\n[black][[red]*[black]] [bright_yellow]Loading [[{count} of {total}]] [bright_blue]{file}")

    def skippingHostAddress(self, file: str):
        self.console.print(
            f"\n[red][[yellow]![red]] [bright_yellow]Host found without IPv4 or UPv6 address in: [bright_blue]{file}[bright_yellow]. Skipping host...")


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
        return f"[bright_green][[yellow]@[bright_green]] [orange3]Results stored in: [bright_green]{os.path.basename(result_file)}\t({result_file})\n"

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


class BannerPrinter:
    "A class for printing banners"

    def __init__(self, logo):
        self.logo = logo
        self.rich_colors = ['black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'bright_black',
                            'bright_red', 'bright_green', 'bright_yellow', 'bright_blue', 'bright_magenta', 'bright_cyan', 'bright_white']
        self.print()

    def print(self) -> None:
        for line in self.logo.split("\n"):
            for character in line:
                if character in ["█"]:
                    rprint(f"[bright_yellow]{character}", end="", flush=True)
                elif character in ["="]:
                    rprint(f"[bright_yellow]{character}", end="", flush=True)
                else:
                    rprint(f"[bright_red]{character}", end="", flush=True)
            print()


class TextOutput():
    def __init__(self):
        self.entries = []

    def addMain(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_NORMAL, Fore.RESET))

    def addHumn(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_FRIENDLY, Style.DIM))

    def addErrr(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_ERROR, Fore.RED))

    def addGood(self, text):
        self.entries.append(TextOutputEntry(
            text, constants.TEXT_SUCCESS, Fore.GREEN))

    def printToConsole(self):
        for line in self.entries:
            shouldPrint = False
            if (line.output == constants.TEXT_NORMAL or line.output == constants.TEXT_ERROR):
                shouldPrint = True
            elif (settings.printHumanFriendlyText):
                shouldPrint = True

            if shouldPrint:
                print(line.getText())


class TextOutputEntry():
    # Output specified the type of output for the text
    #   0 - Main output
    #   1 - Unnecessary but friendly output (e.g. headings)
    #   2 - Error output
    #   3 - Success/Good output
    def __init__(self, text, output, colour):
        self.text = text
        self.output = output
        self.colour = colour

    def getText(self):
        if settings.colourSupported:
            return "%s%s%s" % (self.colour, self.text, Style.RESET_ALL)
        else:
            return self.text
