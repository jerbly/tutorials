import sys
sys.path.append('/home/pi/py/Adafruit-Raspberry-Pi-Python-Code/Adafruit_CharLCDPlate')
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import threading
import time
import textwrap
import subprocess

api_key='---'
api_secret='---'

access_token_key='---'
access_token_secret='---'


class DisplayLoop(StreamListener):
    """
    This class is a listener for tweet stream data. It's also callable so it
    can run the main display thread loop to update the display.
    """
    def __init__(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.backlight(self.lcd.RED)
        self.lcd.clear()
        self.backlight_map = {'clarkson':self.lcd.RED,
                              'pearl':self.lcd.GREEN,
                              'love':self.lcd.BLUE,
                              'hate':self.lcd.YELLOW,
                              'kyle':self.lcd.TEAL,
                              'like':self.lcd.VIOLET}
        self.msglist = []
        self.pos = 0
        self.tweet = 'Nothing yet'
        
    def set_backlight(self):
        words = self.tweet.lower().split(' ')
        use_default = True
        for w in words:
            if w in self.backlight_map:
                self.lcd.backlight(self.backlight_map[w])
                use_default = False
                break    
        if use_default:
            self.lcd.backlight(self.lcd.WHITE)
        
    def on_data(self, data):
        tweet_data = json.loads(data)
        self.tweet = tweet_data['text'].encode('ascii', errors='backslashreplace')
        self.msglist = [x.ljust(16) for x in textwrap.wrap(str(self.tweet),16)]
        self.pos = 0
        self.set_backlight()
        self.scroll_message()
        return True

    def on_error(self, status):
        print status
        
    def write_message(self,msg):
        self.lcd.home()
        self.lcd.message(msg)

    def scroll_message(self):
        "Displays the page of text and updates the scroll position for the next call"
        if len(self.msglist) == 0:
            self.write_message(''.ljust(16)+'\n'+''.ljust(16))
        elif len(self.msglist) == 1:
            self.write_message(self.msglist[0]+'\n'+''.ljust(16))
        elif len(self.msglist) == 2:
            self.write_message(self.msglist[0]+'\n'+self.msglist[1])
        else:
            if self.pos >= len(self.msglist)-1:
                self.pos = 0
            else:
                self.write_message(self.msglist[self.pos]+'\n'+self.msglist[self.pos+1])
                self.pos+=1        
            
    def get_ip_address(self,interface):
        "Returns the IP address for the given interface e.g. eth0"
        try:
            s = subprocess.check_output(["ip","addr","show",interface])
            return s.split('\n')[2].strip().split(' ')[1].split('/')[0]
        except:
            return '?.?.?.?'        
        
    def __call__(self):
        while True:
            if self.lcd.buttonPressed(self.lcd.LEFT):
                self.write_message(self.get_ip_address('eth0').ljust(16)+'\n'+self.get_ip_address('wlan0').ljust(16))
            else:
                self.scroll_message()
            time.sleep(1)

display_loop_instance = DisplayLoop()

# Start the thread running the callable
threading.Thread(target=display_loop_instance).start()

# Log in to twitter and start the tracking stream
auth = OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token_key, access_token_secret)
stream = Stream(auth, display_loop_instance)
stream.filter(track=['jeremy'])
