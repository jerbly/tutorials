'''
Created on Jul 26, 2014

@author: jeremyblythe
'''
import sys
sys.path.append('/home/pi/Adafruit-Raspberry-Pi-Python-Code/Adafruit_ADS1x15')

import pygame
import os
import pygameui as ui
import logging
import RPi.GPIO as GPIO
import signal
from Adafruit_ADS1x15 import ADS1x15
import threading
import time

ADS1015 = 0x00  # 12-bit ADC
ADS1115 = 0x01  # 16-bit ADC

# Select the gain
# gain = 6144  # +/- 6.144V
gain = 4096  # +/- 4.096V
# gain = 2048  # +/- 2.048V
# gain = 1024  # +/- 1.024V
# gain = 512   # +/- 0.512V
# gain = 256   # +/- 0.256V

# Select the sample rate
sps = 8    # 8 samples per second
# sps = 16   # 16 samples per second
# sps = 32   # 32 samples per second
# sps = 64   # 64 samples per second
# sps = 128  # 128 samples per second
# sps = 250  # 250 samples per second
# sps = 475  # 475 samples per second
# sps = 860  # 860 samples per second

# Initialise the ADC using the default mode (use default I2C address)
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
adc = ADS1x15(ic=ADS1115)

#Setup the GPIOs as outputs - only 4 and 17 are available
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(17, GPIO.OUT)

log_format = '%(asctime)-6s: %(name)s - %(levelname)s - %(message)s'
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(log_format))
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

MARGIN = 20

class PotReader():
    def __init__(self, pitft):
        self.pitft = pitft
        self.terminated = False
        
    def terminate(self):
        self.terminated = True
        
    def __call__(self):
        while not self.terminated:
            # Read channel 0 in single-ended mode using the settings above
            volts = adc.readADCSingleEnded(0, gain, sps) / 1000
            self.pitft.set_volts_label(volts)
            self.pitft.set_progress(volts / 3.3)

class PiTft(ui.Scene):
    def __init__(self):
        ui.Scene.__init__(self)

        self.on17_button = ui.Button(ui.Rect(MARGIN, MARGIN, 130, 60), '17 on')
        self.on17_button.on_clicked.connect(self.gpi_button)
        self.add_child(self.on17_button)

        self.on4_button = ui.Button(ui.Rect(170, MARGIN, 130, 60), '4 on')
        self.on4_button.on_clicked.connect(self.gpi_button)
        self.add_child(self.on4_button)

        self.off17_button = ui.Button(ui.Rect(MARGIN, 100, 130, 60), '17 off')
        self.off17_button.on_clicked.connect(self.gpi_button)
        self.add_child(self.off17_button)

        self.off4_button = ui.Button(ui.Rect(170, 100, 130, 60), '4 off')
        self.off4_button.on_clicked.connect(self.gpi_button)
        self.add_child(self.off4_button)

        self.progress_view = ui.ProgressView(ui.Rect(MARGIN, 200, 280, 40))
        self.add_child(self.progress_view)

        self.volts_value = ui.Label(ui.Rect(135, 170, 50, 30), '')
        self.add_child(self.volts_value)

    def gpi_button(self, btn, mbtn):
        logger.info(btn.text)
        
        if btn.text == '17 on':
            GPIO.output(17, False)
        elif btn.text == '4 on':
            GPIO.output(4, False)
        elif btn.text == '17 off':
            GPIO.output(17, True)
        elif btn.text == '4 off':
            GPIO.output(4, True)

    def set_progress(self, percent):
        self.progress_view.progress = percent
        
    def set_volts_label(self, volts):
        self.volts_value.text = '%.2f' % volts

    def update(self, dt):
        ui.Scene.update(self, dt)


ui.init('Raspberry Pi UI', (320, 240))
pygame.mouse.set_visible(False)

pitft = PiTft()

# Start the thread running the callable
potreader = PotReader(pitft)
threading.Thread(target=potreader).start()

def signal_handler(signal, frame):
    print 'You pressed Ctrl+C!'
    potreader.terminate()
    sys.exit(0)
        
signal.signal(signal.SIGINT, signal_handler)

ui.scene.push(pitft)
ui.run()


