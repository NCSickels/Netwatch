import threading
from modules import *
from bs4 import BeautifulSoup
from rich.console import Console
import datetime
import random
from modules import sites, soft404_indicators, user_agents


class Sagemode:
    """Sagemode Jutsu: Simple and Effective OSINT Username Search Tool"""

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
        self.colorConfig = ColorConfig()
        self.console = Console()
        self.configManager = ConfigManager()
        self.lamePrint = LamePrint()
        self.logger = Logger()
        self.notifySagemode = NotifySagemode()
        self.positive_count = 0
        self.usernamePrompt = "\nEnter target username: "
        self.username = input(self.usernamePrompt)
        self.resultDir = self.configManager.getPath("sagemode", "datadir")
        self.result_file = self.resultDir + self.username + ".txt"
        self.found_only = False
        self.__version__ = "1.1.3"
        # self.start(self.sagemodeLogo, self.sagemodeLogoText, delay=0.001)

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
            # self.notify.previousContextMenu("Information Gathering")
            return
        except Exception:
            self.console.print_exception()
