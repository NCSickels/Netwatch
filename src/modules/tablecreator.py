import os
import json
from rich.console import Console
from rich.table import Table


class TableCreator:
    "A class for creating help menu tables from JSON data"

    def __init__(self, jsonFile=None):
        self.console = Console()
        self.jsonFile = os.path.dirname(os.path.abspath(
            __file__)) + '/../json/menuData.json'  # if jsonFile is None else jsonFile

    @staticmethod
    def readJson(file_path: str) -> dict:
        with open(file_path) as f:
            data = json.load(f)
            return data

    def createTable(self, header_data: dict, column_data: list, row_data: list, column_keys: list) -> None:
        table = Table(
            show_header=header_data.get("show_header", True),
            header_style=header_data.get("header_style", "bold white"),
            title=header_data.get("title", ""),
            width=int(header_data.get("width", 84)),
            show_lines=True)
        for i, column in enumerate(column_data):
            table.add_column(
                column.get("title", ""),
                style=column.get("style", ""),
                justify=column.get("justify", "right"),
                width=column.get("width", 30))
        column_keys += [None] * (len(column_data) - len(column_keys))
        for row in row_data:
            row_values = [str(row.get(column_keys[i], ""))
                          for i in range(len(column_data))]
            table.add_row(*row_values)
        return table

    def displayTable(self, jsonData: dict, module: str) -> None:
        column_keys_dict = {
            "Main": ["option", "modules", "description"],
            "Core": ["command", "description"],
            "Information_Gathering": ["option", "modules", "description"],
            "Nmap_Scans": ["type", "options", "description"],
            "Nmap_Commands": ["command", "description"],
            "DataParser": ["command", "description"],
        }
        for table in jsonData[module]:
            header_data = table.get("header", [{}])[0]
            column_data = table.get("columns", [])
            row_data = table.get("rows", [])
            column_keys = column_keys_dict.get(module, [])
            table = self.createTable(
                header_data, column_data, row_data, column_keys)
            self.console.print(table)
            print("\n")

    def displayTableFromFile(self, module: str) -> None:
        jsonData = self.readJson(self.jsonFile)
        self.displayTable(jsonData, module)
