import re
import requests
import os
import subprocess

from rich.console import Console
from config import ConfigManager
from modules.termutils import Color
from logger import Logger


class UpdateHandler:
    """A class for handling updates for the Netwatch tool"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.console = Console()
        self.logger = Logger()

        self.local_version = self.config_manager.get(
            "general_config", "__version__")

    def check_update(self) -> None:
        try:
            # Add support for deprecated config file type
            file_names = ["netwatch.ini", "netwatch.cfg"]
            remote_version = None

            for file_name in file_names:
                url = (
                    f'https://raw.githubusercontent.com/NCSickels/Netwatch/main/src/config/{file_name}')
                r = requests.get(url)
                if r.status_code == 200:
                    matches = re.findall('__version__\s*=\s*([\d.]+)', r.text)
                    if matches:
                        remote_version = str(matches[0])
                        break
                    else:
                        raise ValueError(
                            f"Unable to find version number in {file_name}")

            if remote_version is not None:
                if self.is_newer_version(remote_version, self.local_version):
                    self.logger.info(f"{Color.NOTICE}Update available!")
                    self.logger.info((f"{Color.NOTICE}You are running Version: " +
                                     f"{Color.OKGREEN + self.local_version}"))
                    self.logger.info((f"{Color.NOTICE}New version available: " +
                                     f"{Color.OKGREEN}{remote_version}{Color.END}"))
                    self.promptForUpdate()
                else:
                    self.logger.info("Netwatch is up to date.\n")
            else:
                raise ValueError("Unable to find any update file")

        except Exception as error:
            self.logger.error(f"Error checking for update: {error}")

    def promptForUpdate(self) -> None:
        response = input(
            "\nWould you like to update Netwatch? [y/n]: ").lower()
        self.update() if response == "y" else None

    def is_newer_version(self, remote_version: str, local_version: str) -> bool:
        remote_version_revisions = list(map(int, remote_version.split('.')))
        local_version_revisions = list(map(int, local_version.split('.')))
        return remote_version_revisions > local_version_revisions

    def update(self) -> None:
        repo_dir = os.path.dirname(os.path.realpath(__file__))
        # ensure we're performing git command in the local git repo directory
        os.chdir(repo_dir)
        subprocess.run(["git", "pull"])
