#!/bin/bash
# Script for updating netwatch tools
# ----------------------------------

clear
echo "

███╗   ██╗███████╗████████╗██╗    ██╗ █████╗ ████████╗ ██████╗██╗  ██╗    
████╗  ██║██╔════╝╚══██╔══╝██║    ██║██╔══██╗╚══██╔══╝██╔════╝██║  ██║    
██╔██╗ ██║█████╗     ██║   ██║ █╗ ██║███████║   ██║   ██║     ███████║    
██║╚██╗██║██╔══╝     ██║   ██║███╗██║██╔══██║   ██║   ██║     ██╔══██║    
██║ ╚████║███████╗   ██║   ╚███╔███╔╝██║  ██║   ██║   ╚██████╗██║  ██║    
╚═╝  ╚═══╝╚══════╝   ╚═╝    ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝    

██╗   ██╗██████╗ ██████╗  █████╗ ████████╗███████╗██████╗     
██║   ██║██╔══██╗██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔══██╗    
██║   ██║██████╔╝██║  ██║███████║   ██║   █████╗  ██████╔╝    
██║   ██║██╔═══╝ ██║  ██║██╔══██║   ██║   ██╔══╝  ██╔══██╗    
╚██████╔╝██║     ██████╔╝██║  ██║   ██║   ███████╗██║  ██║    
 ╚═════╝ ╚═╝     ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝    
";

git clone --depth=1 https://github.com/NCSickels/netwatch.git
sudo chmod +x netwatch/install.sh
bash netwatch/install.sh

