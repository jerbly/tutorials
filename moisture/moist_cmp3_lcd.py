import sys
sys.path.append('/home/pi/py/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate')

from time import sleep
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import mcp3008
from controlmypi import ControlMyPi
import logging
import datetime
import pickle
from genericpath import exists

lcd = Adafruit_CharLCDPlate()

PICKLE_FILE = '/home/pi/py/moisture/moist.pkl'

def on_msg(conn, key, value):
    pass

def append_chart_point(chart, point):
    if len(chart) >= 48:
        del chart[0]
    chart.append(point)
    return chart

def save(data):
    output = open(PICKLE_FILE, 'wb')
    pickle.dump(data, output)
    output.close()

def load(default):
    if not exists(PICKLE_FILE):
        return default
    pkl_file = open(PICKLE_FILE, 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()
    return data

def update_lcd(m):
    try:
        lcd.home()
        lcd.message("Moisture level:\n%d%%   " % m)
        if m < 15:
            lcd.backlight(lcd.RED)
        elif m < 50:
            lcd.backlight(lcd.YELLOW)
        else:
            lcd.backlight(lcd.GREEN)
    except IOError as e:
        print e

logging.basicConfig(level=logging.INFO)

p = [ 
    [ ['G','moist','% level',0,0,100], ['LC','chart1','Time','Value',0,100] ], 
    ]

c1 = load([])

readings = []

conn = ControlMyPi('you@gmail.com', 'password', 'moisture3', 'Moisture monitor 3', p, on_msg)

delta = datetime.timedelta(minutes=30)
next_time = datetime.datetime.now()

if conn.start_control():
    try:
        while True:
            dt = datetime.datetime.now()
            m = mcp3008.read_pct(5)
            readings.append(m)
            update_lcd(m)
            to_update = {'moist':m}
            if dt > next_time:       
                # Take the average from the readings list to smooth the graph a little
                avg = int(round(sum(readings)/len(readings)))             
                readings = []   
                c1 = append_chart_point(c1, [dt.strftime('%H:%M'), avg])                         
                save(c1)
                next_time = dt + delta
                to_update['chart1'] = c1
            conn.update_status(to_update)
            sleep(30)
    finally:
        conn.stop_control()
