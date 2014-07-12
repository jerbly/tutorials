'''
Created on Jul 12, 2014

@author: jeremyblythe
'''
import pygame
import os
from time import sleep

os.putenv('SDL_FBDEV', '/dev/fb1')
pygame.init()
lcd = pygame.display.set_mode((320, 240))
lcd.fill((255,0,0))
pygame.display.update()
sleep(1)

pygame.mouse.set_visible(False)

lcd.fill((0,0,0))
pygame.display.update()