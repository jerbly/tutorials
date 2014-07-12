'''
Created on Jul 12, 2014

@author: jeremyblythe
'''
import pygame
import os
from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

button_map = {23:(255,0,0), 22:(0,255,0), 27:(0,0,255), 18:(0,0,0)}

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((320, 240))
lcd.fill((0,0,0))
pygame.display.update()

while True:
    # Scan the buttons
    for (k,v) in button_map.items():
        if GPIO.input(k) == True:
            lcd.fill(v)
            pygame.display.update()
    sleep(0.1)    

