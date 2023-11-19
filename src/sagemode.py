import aiohttp
import asyncio
import threading
import random
import datetime
import os
from bs4 import BeautifulSoup
from rich.console import Console
from accessories import Notify
from sites import sites, soft404_indicators, user_agents


class Sagemode:
    sagemodeLogo = '''
       ____                __  ___        __
      / __/__ ____ ____   /  |/  /__  ___/ /__
     _\ \/ _ `/ _ `/ -_) / /|_/ / _ \/ _  / -_)
    /___/\_,_/\_, /\__/ /_/  /_/\___/\_,_/\__/
             /___/

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

    def __init__(self, username: str):
        self.username = username
        self.positive_results = []
        self.positive_count = 0
        self.console = Console()
        self.notify = Notify()
        self.found_only = False
        self.result_file = os.path.join("data", f"{self.username}.txt")

    async def check_site(self, site: str, url: str, headers):
        url = url.format(self.username)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    text = await response.text()
                    if (
                        response.status == 200
                        and self.username.lower() in text.lower()
                        and not self.is_soft404(text)
                    ):
                        with threading.Lock():
                            self.positive_count += 1
                        self.console.print(self.notify.found(site, url))
                        self.positive_results.append(url)
                    else:
                        if not self.found_only:
                            self.console.print(self.notify.not_found(site))
        except Exception as e:
            self.notify.exception(site, e)

    def isSoft404(self, text: str) -> bool:
        soup = BeautifulSoup(text, "html.parser")
        title = soup.title.string.lower() if soup.title else ""
        return "page not found" in title

    async def start(self):
        current_datetime = datetime.datetime.now()
        date = current_datetime.strftime("%m/%d/%Y")
        time = current_datetime.strftime("%I:%M:%p")
        headers = {"User-Agent": random.choice(user_agents)}
        # sites = self.load_sites()
        self.positive_results = []

        with self.console.status(
            f'[*] Searching for target: {self.username}', spinner="bouncingBall"
        ):
            tasks = [
                self.check_site(site, url, headers) for site, url in sites.items()
            ]
            await asyncio.gather(*tasks)
        with open(self.result_file, 'a') as f:
            for url in self.positive_results:
                f.write(f'{url}\n')


def main():
    if not os.path.exists("data"):
        os.mkdir("data")
    username = input("Enter the username: ")
    sagemode = Sagemode(username)
    asyncio.run(sagemode.start())


if __name__ == "__main__":
    main()
