# Define the Python commands (assuming python.exe is in PATH, or use full path if needed)
$command1 = "python discord_server.py"
$command2 = "python main.py --symbol 'AAPL'"
$command3 = "python main.py --symbol 'META'"

# Create the argument list for Windows Terminal with tabs, running python.exe directly
$wtArgs = "-w 0 nt $command1 ; nt $command2 ; nt $command3"

# Launch Windows Terminal with all tabs
Start-Process wt -ArgumentList $wtArgs