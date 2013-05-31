from time import sleep
import mcp3008

# ANSI escape codes
PREVIOUS_LINE="\x1b[1F"
RED_BACK="\x1b[41;37m"
GREEN_BACK="\x1b[42;30m"
YELLOW_BACK="\x1b[43;30m"
RESET="\x1b[0m"

# Clear the screen and put the cursor at the top
print '\x1b[2J\x1b[H'
print 'Moisture sensor'
print '===============\n'

while True:
    m = mcp3008.readadc(5)
    if m < 150:
        background = RED_BACK
    elif m < 500:
        background = YELLOW_BACK
    else:
        background = GREEN_BACK
    print PREVIOUS_LINE + background + "Moisture level: {:>5} ".format(m) + RESET
    sleep(.5)
