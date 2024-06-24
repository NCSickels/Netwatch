#!/usr/bin/python3
#
#
#
# ███╗   ██╗███████╗████████╗██████╗ ██████╗ ███████╗ █████╗  ██████╗██╗  ██╗
# ████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║
# ██╔██╗ ██║█████╗     ██║   ██████╔╝██████╔╝█████╗  ███████║██║     ███████║
# ██║╚██╗██║██╔══╝     ██║   ██╔══██╗██╔══██╗██╔══╝  ██╔══██║██║     ██╔══██║
# ██║ ╚████║███████╗   ██║   ██████╔╝██║  ██║███████╗██║  ██║╚██████╗██║  ██║
# ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
#
#
#   Netbreach v0.1
#   by @NCSickels
#

import os
import json
import urllib3
import requests
import argparse
from tabulate import tabulate
from requests import ConnectionError
from modules.logos import NETBREACH_LOGO
from logger import Logger

urllib3.disable_warnings()


class Netbreach:
    def __init__(self):
        self.logger = Logger()

    def find_leaks_proxynova(self, email, proxy, number):
        url = f"https://api.proxynova.com/comb?query={email}"
        headers = {'User-Agent': 'curl'}
        session = requests.session()

        if proxy:
            session.proxies = {'http': proxy, 'https': proxy}

        response = session.get(url, headers=headers, verify=False)

        if response.status_code == 200:
            data = json.loads(response.text)
            total_results = data.get("count", 0)
            self.logger.info(
                f'Found {total_results} different records in database.')

            lines = data.get("lines", [])[:number]
            return lines
        else:
            self.logger.error(f'Failed to fetch results from ProxyNova. Status code:' +
                              f'{response.status_code}\n')
            return []

    def find_leaks_local_db(self, database, keyword, number):
        if not os.path.exists(database):
            self.logger.error(f'Local database file not found: {database}\n')
            exit(-1)

        if database.endswith('.json'):
            with open(database, 'r') as json_file:
                try:
                    data = json.load(json_file)
                    lines = data.get("lines", [])
                except json.JSONDecodeError:
                    self.logger.error(
                        f'Failed to parse local database as JSON.\n')
                    exit(-1)
        else:
            file_length = os.path.getsize(database)
            block_size = 1
            line_count = 0
            results = []

            try:
                with open(database, 'r') as file:
                    while True:
                        block = [next(file).strip() for _ in range(block_size)]
                        line_count += len(block)

                        if not block or line_count > file_length:
                            break

                        filtered_block = [
                            line for line in block if keyword.lower() in line.lower()]
                        results.extend(filtered_block)

                        self.logger.info(
                            f'Reading {line_count} lines in database...')

                        if number is not None and len(results) >= number:
                            break

            except KeyboardInterrupt:
                print("\n Bye.\n")
                exit(-1)

            except:
                pass

            return results[:number] if number is not None else results

    def main(self, database, keyword, output=None, proxy=None, number=20):
        self.logger.info(
            f'Searching for {keyword} leaks in {database}..')

        if database.lower() == "proxynova":
            results = self.find_leaks_proxynova(keyword.strip(), proxy, number)
        else:
            results = self.find_leaks_local_db(
                database.strip(), keyword.strip(), number)

        if not results:
            self.logger.info(f'No leaks found in {database}!\n')
        else:
            self.print_results(results, output, number)

    def print_results(self, results, output, number):
        self.logger.info(
            f'Selecting the first {len(results)} results..')

        headers = ["Username@Domain", "Password"]
        table_data = []

        for line in results:
            parts = line.split(":")
            if len(parts) == 2:
                username_domain, password = parts
                table_data.append([username_domain, password])

        if output is not None:
            if output.endswith('.json'):
                with open(output, 'w') as json_file:
                    json.dump({"lines": results}, json_file, indent=2)
                    self.logger.info(
                        f'Data saved successfully in {output}!\n')
            else:
                with open(output, 'w') as txt_file:
                    txt_file.write(
                        tabulate(table_data, headers, showindex="never"))
                    self.logger.info(
                        f'Data saved successfully in {output}!\n')
        else:
            self.logger.info('Done.\n')
            print(tabulate(table_data, headers, showindex="never"))
            print()


if __name__ == '__main__':
    print(NETBREACH_LOGO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--database", default="ProxyNova",
                        help="Database used for the search (ProxyNova or LocalFile)")
    parser.add_argument(
        "-k", "--keyword", help="Keyword (user/domain/pass) to search for leaks in the DB")
    parser.add_argument("-n", "--number", type=int, default=20,
                        help="Number of results to show (default is 20)")
    parser.add_argument(
        "-o", "--output", help="Save the results as json or txt into a file")
    parser.add_argument(
        "-p", "--proxy", help="Set HTTP/S proxy (like http://localhost:8080)")
    args = parser.parse_args()

    if not args.keyword:
        parser.print_help()
        exit(-1)

    logger = Logger()

    try:
        netbreach = Netbreach()
        netbreach.main(args.database, args.keyword,
                       args.output, args.proxy, args.number)

    except ConnectionError:
        logger.error(
            'Can\'t connect to service! Check your internet connection.\n')

    except KeyboardInterrupt:
        print('\n Bye.\n')
        exit(-1)

    except Exception as e:
        logger.error(f'An error occurred: {e}\n')
