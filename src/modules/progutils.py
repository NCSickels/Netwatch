from config import ConfigManager
from logger import Logger
from .updatehandler import UpdateHandler
from .banners import print_banner
from .termutils import Color


import sys
import os
import glob
from time import sleep


# Utility Class
class Program:
    """A class for main program functions"""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.update_handler = UpdateHandler()
        self.logger = Logger()
        self.version = ConfigManager().get("general_config", "__version__")

    def start(self) -> None:
        self.clear_screen()
        print_banner()
        # print(NETWATCH_BANNER.format(version=self.version))
        self.update_handler.check_update()
        self.create_folders([("general_config", "tooldir"),
                            ("general_config", "scandir"),
                            ("sagemode", "datadir")])

    def create_folders(self, paths: list) -> None:
        for section, option in paths:
            path = self.config_manager.get_path(section, option)
            if not os.path.isdir(path):
                os.makedirs(path)

    def end(self) -> None:
        print("\n Bye.\n")
        sleep(0.25)
        sys.exit()

    def clean(self, path: str) -> None:
        _full_path = os.path.basename(os.path.normpath(path))
        self.logger.info('Cleaning directories...')
        if os.path.exists(path):
            deleted_files = False
            if os.path.exists(path):
                for root, dirs, files in os.walk(path, topdown=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            os.remove(file_path)
                            self.logger.info(f'Deleted file: {file_path}')
                            deleted_files = True
                        except Exception as e:
                            print(e)
                    for dir in dirs:
                        dir_path = os.path.join(root, dir)
                        try:
                            os.rmdir(dir_path)
                            deleted_files = True
                        except Exception as e:
                            print(e)
                # os.rmdir(path)
                if deleted_files:
                    self.logger.info(
                        f'Directory:{_full_path} successfully cleaned.')
                else:
                    self.logger.info(f'No files found in {_full_path}.')
            else:
                raise FileNotFoundError(
                    f'{Color.RED}{path} directory not found!{Color.END}\n')
        else:
            raise FileNotFoundError(
                f'{Color.RED}Path {path} does not exist!{Color.END}\n')

    def print_path(self, module: str) -> None:
        _split_module = module.split("/")
        if (len(_split_module) <= 1):  # if module is in root directory (Netwatch/)
            print(f'\n[*] Module -> {_split_module[0]}')
            print(f'[*] Path   -> {module+"/"}\n')
            # self.logger.info(
            #     f'Module -> {_split_module[0]}\n')
            # self.logger.info(f'Path   -> {module+"/"}')
        else:
            print(f'\n[*] Module -> {_split_module[len(_split_module)-1]}')
            print(f'[*] Path   -> {module+"/"}\n')
            # self.logger.info(
            #     f'\nModule -> {_split_module[len(_split_module)-1]}')
            # self.logger.info(f'Path   -> {module+"/"}')

    def clear_screen(self) -> None:
        print("\033[H\033[J", end="")
        # os.system('cls' if os.name == 'nt' else 'clear')

    def find_files(self, file_type: any, directory='/') -> str:
        self.logger.info(f'Searching for {file_type} files...')
        try:
            search_path = os.path.join(directory, '**/*'+file_type)
            files = glob.glob(search_path, recursive=True)
            if not files:
                self.logger.warning(f'No {file_type} files found.')
                return
            for filename in files:
                self.logger.info(f'Found file {filename}')
                response = input("Use this file? [y/n]: ").lower()
                if response in ["y", "yes"]:
                    self.config_manager.set(
                        "general_config", "ovpn_path", filename)
                    self.logging.info(f'Selected file {filename}')
                    return filename
            self.logger.warning(
                (f'No other {file_type} files found. Please manually add path to .ini file.'))
        except Exception as e:
            self.logger.error(f'An error occurred: {e}')
            self.logger.warning(f'No {file_type} files found!')

    def __del__(self):
        # sys.stdout = self.original_stdout
        # self.log_file.close()
        pass
