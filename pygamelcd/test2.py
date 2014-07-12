'''
Created on Jul 12, 2014

@author: jeremyblythe
'''
import pygame
import os
from time import sleep
import RPi.GPIO as GPIO

#Note #21 changed to #27 for rev2 Pi
button_map = {23:(255,0,0), 22:(0,255,0), 27:(0,0,255), 18:(0,0,0)}

#Setup the GPIOs as inputs with Pull Ups since the buttons are connected to GND
GPIO.setmode(GPIO.BCM)
for k in button_map.keys():
    GPIO.setup(k, GPIO.IN, pull_up_down=GPIO.PUD_UP)

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((320, 240))
lcd.fill((0,0,0))
pygame.display.update()

while True:
    # Scan the buttons
    for (k,v) in button_map.items():
        if GPIO.input(k) == False:
            lcd.fill(v)
            pygame.display.update()
    sleep(0.1)    

