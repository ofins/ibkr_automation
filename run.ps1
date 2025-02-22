# Define the Python commands (assuming python.exe is in PATH, or use full path if needed)
$command1 = "python discord_server.py"
$command2 = "python main.py --symbol AAPL --menu 4"
$command3 = "python main.py --symbol META --menu 4"
$command4 = "python main.py --symbol AMD --menu 4"
$command5 = "python main.py --symbol MU --menu 4"
$command6 = "python main.py --menu 1"

# Create the argument list for Windows Terminal with tabs, running python.exe directly
$wtArgs = "-w 0 nt $command1 ; nt $command2 ; nt $command3; nt $command4; nt $command5; nt $command6"

# Launch Windows Terminal with all tabs
Start-Process wt -ArgumentList $wtArgs