import sys
sys.path.append('/home/pi/py/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate')

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import mcp3008

lcd = Adafruit_CharLCDPlate()

while True:
    m = mcp3008.readadc(5)
    try:
        lcd.home()
        lcd.message("Moisture level:\n%d    " % m)
        if m < 150:
            lcd.backlight(lcd.RED)
        elif m < 500:
            lcd.backlight(lcd.YELLOW)
        else:
            lcd.backlight(lcd.GREEN)
    except IOError as e:
        print e
    sleep(.5)
