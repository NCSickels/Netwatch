#!/usr/bin/env python3
#
#
# ███╗   ██╗███████╗████████╗██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗
# ████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
# ██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║███████║   ██║   ██║     ███████║
# ██║╚██╗██║██╔══╝     ██║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║
# ██║ ╚████║███████╗   ██║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║
# ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
#
#
#   Netwatch v2.0
#   by: @NCSickels

# Imports
import sys
import os
import configparser
import time


# Common Functions


class Color:
    HEADER = '\033[95m'
    IMPORTANT = '\33[35m'
    NOTICE = '\033[33m'
    BLUE = '\033[34m'  # [1;34m]
    OKBLUE = '\033[94m'
    GREEN = '\033[32m'  # [1;32m]
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    UNDERLINE = '\033[4m'
    BOLD = '\033[1m'
    LOGGING = '\33[34m'


class Utilities:
    command_history = set()

    def __init__(self):
        pass

    def clearScr() -> None:
        if (os.name == 'posix'):
            os.system('clear')
        else:
            os.system('cls')

    def commandHistoryUpdate(command: str) -> None:
        Utilities.command_history.add(command)

    def commandHistoryPrint() -> None:
        print("\n")
        i = 0
        for command in Utilities.command_history:
            print(f"{i}: {command}")
            i += 1
        print("\n")

    def endProgram() -> None:
        print(" Finishing up...\n")
        with open(configFile, 'w') as configfile:
            config.write(configfile)
        time.sleep(0.25)
        sys.exit()


# Start Menu Classes


class Netwatch:
    netwatchLogo = '''
                    :!?Y5PGGPP5!:             .!JPGBGPY7^.                      
                  ..J#@#Y!75#@@@&P7:     .~7?5#@@&BY77YG#BY:                    
                  .^7~^.    .!P&@@@&BJ: .7B&@@@@G7.     :!Y!                    
                               :?G&@&Y: :5@&#BJ^       ..                       
                   !J!.   .:~!~^  :~^.   .^^:..:~!!~:  ..YJ.                    
                   7B~ .~5#&@@@&BJ:  .:  .. .JB&@@@@&G~  ~#!                    
                  .77. !#@@@@@@@@&7  ?Y  J? ^B@@@@&&&@B: :!:                    
                     .^JY?!~~!?PB!   5J  ?P. !BP?!^::^!!^                       
                    ::.         .^.~YJ:  .?Y!~:         .:.                     
                 .^JG~           :5?:  ..  .75^          ?G?:                   
               .:J&@Y            !Y   ....   ?~          :B@B~.                 
               ^5@@@G^       .:!J5G57.   .~YGG5?!:.     .^G@@@?                 
              .J&@@@@#57~~!YBB&@@@@@@BJ7JG@@@@@@@&BPJ775B#@@@&P.                
               :#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@B7                 
               .J@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@GJ:                 
                .!P#&&&@@@@@@@@@&&&&@@@@@@@@&#&&@@@@@@@@@&P?^.                  
                   .:^^~!!!!YB@&&G5J?7!!?JYJ?JPPPPJ777!~~^.                     
                             :Y#@@@@&#BBBB#&@@&#J^                              
                               :75B&&&&@@&&&BY!:.                               
                                  .:::^^^^:::.   
===================================================================================
       ███╗   ██╗███████╗████████╗██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗
       ████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║
       ██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║███████║   ██║   ██║     ███████║
       ██║╚██╗██║██╔══╝     ██║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║
       ██║ ╚████║███████╗   ██║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║
       ╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝
===================================================================================W
'''

    def __init__(self):
        pass


if __name__ == "__main__":
    try:
        installDir = os.path.dirname(os.path.abspath(__file__)) + '/'
        configFile = installDir + "/netwatch.cfg"
        print(installDir)
        config = configparser.ConfigParser()
        config.read(configFile)
        toolDir = installDir + config.get('netwatch', 'toolDir')
        logDir = installDir + config.get('netwatch', 'logDir')
        # yes = config.get('netwatch', 'yes').split()

        file_path = installDir + "/main_helpmenu_table_data.json"
        # json_data = Utilities.readJson(file_path)
        # randomColor = [Color.HEADER, Color.IMPORTANT, Color.NOTICE, Color.BLUE, Color.OKBLUE,
        #            Color.OKGREEN, Color.WARNING, Color.RED, Color.END, Color.UNDERLINE, Color.BOLD, Color.LOGGING]
        # random.shuffle(randomColor)

        Utilities.clearScr()

        netwatchPrompt = "netwatch ~# "
        print(Netwatch.netwatchLogo)
        Netwatch()
    except KeyboardInterrupt:
        Utilities.endProgram()
