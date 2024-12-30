<!-- markdownlint-disable MD033 -->
<!-- markdownlint-disable MD029 -->

# Netwatch - Automated Attack Framework

<p align="center">

<!-- ![Netwatch Temporary Banner](.assets/netwatch-banner.jpg) -->
<img src=".assets/netwatch-banner.jpg" alt="Netwatch Temporary Banner" width="100%">

![Static Badge](https://img.shields.io/badge/Platform-Kali-blue?style=plastic&logo=kalilinux&logoSize=auto)
![Static Badge](https://img.shields.io/badge/Platform-Ubuntu-blue?style=plastic&logo=ubuntu&logoSize=auto)
[![Static Badge](https://img.shields.io/badge/Python%203.12+-FFDE57?style=plastic&label=Requirement&link=https%3A%2F%2Fwww.python.org%2Fdownloads)](https://www.python.org/downloads)
![Static Badge](https://img.shields.io/badge/Bash-white?style=plastic&logo=gnubash&logoColor=grey)
![Static Badge](https://img.shields.io/badge/Docker-blue?style=plastic&logo=docker&logoColor=white)

</p>

## Table of Contents

## Features

### Automated HackTheBox & TryHackMe Basic Initial Enumeration

### Custom Colorized Logger Wrapper

### Nmap Scan Parser

### Netbreach - Breach Searching Tool

## Roadmap

- Web based front end.
- Feroxbuster
- jok3r
- Expliot - IOT Pentesting Framework
- SEToolKit
- Caldera

## Known Issues

- Some longer scans can cause the Nmap Parser to produce a type error due to possible ANSI escape codes in the output.
- Some hosts with a large number of open ports can cause an issue with the "list" command in the Nmap Parser.
