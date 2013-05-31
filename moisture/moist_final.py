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
import smtplib

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

def send_gmail(from_name, sender, password, recipient, subject, body):
    '''Send an email using a GMail account.'''
    senddate=datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    msg="Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, from_name, sender, recipient, subject)
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, recipient, msg+body)
    server.quit()

logging.basicConfig(level=logging.INFO)

p = [ 
    [ ['G','moist','level',0,0,100], ['LC','chart1','Time','Value',0,100] ], 
    ]

c1 = load([])

readings = []

conn = ControlMyPi('you@gmail.com', 'password', 'moisture', 'Moisture monitor', p, on_msg)

delta = datetime.timedelta(minutes=30)
next_time = datetime.datetime.now()

delta_email = datetime.timedelta(days=1)
next_email_time = datetime.datetime.now()

if conn.start_control():
    try:
        while True:
            dt = datetime.datetime.now()
            m = mcp3008.read_pct(5)
            readings.append(m)
            update_lcd(m)
            to_update = {'moist':m}
            
            # Update the chart?
            if dt > next_time:
                # Take the average from the readings list to smooth the graph a little
                avg = int(round(sum(readings)/len(readings)))             
                readings = []   
                c1 = append_chart_point(c1, [dt.strftime('%H:%M'), avg])
                save(c1)
                next_time = dt + delta
                to_update['chart1'] = c1
            conn.update_status(to_update)
            
            #Send an email?
            if dt > next_email_time:
                next_email_time = dt + delta_email
                if m < 40:
                    send_gmail('Your Name', 'you@gmail.com', 'password', 'recipient@email.com', 'Moisture sensor level', 'The level is now: %s' % m)
            
            sleep(30)
    finally:
        conn.stop_control()
