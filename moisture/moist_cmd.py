from time import sleep
import mcp3008

while True:
    m = mcp3008.readadc(5)
    print "Moisture level: {:>5} ".format(m)
    sleep(.5)
