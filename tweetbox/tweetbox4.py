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
import tornado.ioloop
import tornado.web
import pickle
from genericpath import exists

api_key='---'
api_secret='---'

access_token_key='---'
access_token_secret='---'

class NullListener(StreamListener):
    def on_data(self, data):
        print data
        
class DisplayLoop(StreamListener):
    """
    This class is a listener for tweet stream data. It's also callable so it
    can run the main display thread loop to update the display.
    """
    PICKLE_FILE = '/home/pi/py/tweetbox.pkl'
    
    def __init__(self):
        self.lcd = Adafruit_CharLCDPlate()
        self.lcd.backlight(self.lcd.RED)
        self.lcd.clear()
        self.track_text = 'jeremy'
        self.backlight_map = {'red':self.lcd.RED,
                              'green':self.lcd.GREEN,
                              'blue':self.lcd.BLUE,
                              'yellow':self.lcd.YELLOW,
                              'teal':self.lcd.TEAL,
                              'violet':self.lcd.VIOLET}
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
        print data
        tweet_data = json.loads(data)
        self.set_text(tweet_data['text'].encode('ascii', errors='backslashreplace'))
                 
    def set_text(self, text):
        self.tweet = text
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

    def write_config(self):
        data = {"track_text":self.track_text, "backlight_map":self.backlight_map}
        output = open(self.PICKLE_FILE, 'wb')
        pickle.dump(data, output)
        output.close()
        
    def read_config(self):
        if exists(self.PICKLE_FILE):
            pkl_file = open(self.PICKLE_FILE, 'rb')
            data = pickle.load(pkl_file)
            pkl_file.close()
            self.track_text = data["track_text"]
            self.backlight_map = data["backlight_map"]
        
    def __call__(self):
        while True:
            if self.lcd.buttonPressed(self.lcd.LEFT):
                self.write_message(self.get_ip_address('eth0').ljust(16)+'\n'+self.get_ip_address('wlan0').ljust(16))
            else:
                self.scroll_message()
            time.sleep(1)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        inverted_map = {v:k for k, v in display_loop_instance.backlight_map.items()}
        self.render("templates/form4.html", 
                    config_track=display_loop_instance.track_text,
                    config_red=inverted_map[Adafruit_CharLCDPlate.RED], 
                    config_green=inverted_map[Adafruit_CharLCDPlate.GREEN],
                    config_blue=inverted_map[Adafruit_CharLCDPlate.BLUE],
                    config_yellow=inverted_map[Adafruit_CharLCDPlate.YELLOW],
                    config_teal=inverted_map[Adafruit_CharLCDPlate.TEAL],
                    config_violet=inverted_map[Adafruit_CharLCDPlate.VIOLET])

    def post(self):
        config_track = self.get_argument("config_track")
        colour_map = {self.get_argument("config_red"):Adafruit_CharLCDPlate.RED,
                      self.get_argument("config_green"):Adafruit_CharLCDPlate.GREEN,
                      self.get_argument("config_blue"):Adafruit_CharLCDPlate.BLUE,
                      self.get_argument("config_yellow"):Adafruit_CharLCDPlate.YELLOW,
                      self.get_argument("config_teal"):Adafruit_CharLCDPlate.TEAL,
                      self.get_argument("config_violet"):Adafruit_CharLCDPlate.VIOLET 
                      }
        set_config(config_track, colour_map)
        #Use a redirect to avoid problems with refreshes in the browser from a form post
        self.redirect("/")


def set_config(track_text, colour_map):
    print "restarting"
    display_loop_instance.set_text("Updating configuration")
    #Kill the old stream asynchronously
    global stream    
    stream.listener = NullListener()
    stream.disconnect()
    
    display_loop_instance.track_text = track_text
    display_loop_instance.backlight_map = colour_map
    display_loop_instance.write_config()

    #Make a new stream
    stream = Stream(auth, display_loop_instance)    
    stream.filter(track=[display_loop_instance.track_text], async=True)
    display_loop_instance.set_text("Updated configuration")
    
application = tornado.web.Application([
    (r"/", MainHandler),
])


display_loop_instance = DisplayLoop()
display_loop_instance.read_config()

# Start the thread running the callable
threading.Thread(target=display_loop_instance).start()

# Log in to twitter and start the tracking stream
auth = OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token_key, access_token_secret)
stream = Stream(auth, display_loop_instance)
stream.filter(track=[display_loop_instance.track_text], async=True)
print "Starting"
application.listen(8888)
tornado.ioloop.IOLoop.instance().start()   
print "Stopping"
stream.disconnect()
