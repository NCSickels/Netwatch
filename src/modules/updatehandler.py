import re
import requests
import os
import subprocess

from rich.console import Console
from config.config import ConfigManager
from modules.notify import Notify


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
            # Add support for deprecated config file type
            file_names = ["netwatch.cfg", "netwatch.ini"]
            remote_version = None

            for file_name in file_names:
                url = (
                    f'https://raw.githubusercontent.com/NCSickels/Netwatch/main/src/{file_name}')
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
                    self.notify.update(remote_version, self.local_version)
                    self.promptForUpdate()
                else:
                    self.notify.upToDate()
            else:
                raise ValueError("Unable to find any update file")

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
