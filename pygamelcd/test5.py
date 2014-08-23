'''
Created on Jul 26, 2014

@author: jeremyblythe
'''
import pygame
import os
import pygameui as ui
import logging
import RPi.GPIO as GPIO

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

        self.progress_view = ui.ProgressView(ui.Rect(MARGIN, 180, 280, 40))
        self.add_child(self.progress_view)

        self.progress = 0

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

    def update(self, dt):
        ui.Scene.update(self, dt)
        self.progress_view.progress = self.progress
        self.progress += 0.01
        if self.progress > 1.0:
            self.progress = 0

ui.init('Raspberry Pi UI', (320, 240))
pygame.mouse.set_visible(False)
ui.scene.push(PiTft())
ui.run()


