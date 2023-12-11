import subprocess
from modules.termutils import Notify


class ProgramInstallationManager:
    "A class for managing installations for various tools used in Netwatch"

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
