import subprocess
from logger import *


class PackageManager:
    """A class for managing installations for various tools used in Netwatch"""

    def __init__(self, program_name):
        self.program_name = program_name
        self.logger = Logger()

    def installed(self) -> bool:
        try:
            subprocess.check_output(["which", self.program_name])
            return True
        except subprocess.CalledProcessError:
            return False

    def installPackage(self) -> bool:
        try:
            subprocess.check_call(
                ["sudo", "apt", "install", "-y", self.program_name])
            return True if self.installed() else False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error installing {self.program_name}")
            self.logger.error(f"Exception occurred: {e}")
            return False

    def checkForPackage(self) -> bool:
        if not self.installed():
            self.logger.warning(
                f"{self.program_name} not found. Attempting to install...")
            return self.installPackage()
        else:
            self.logger.info(
                f"{self.program_name} found. Skipping installation.")
            return True
