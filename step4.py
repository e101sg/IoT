#!/usr/bin/env python

# This code is written by Stephen C Phillips.
# It is in the public domain, so you can do what you like with it
# but a link to http://scphillips.com would be nice.

from move import Motor
from move import *
import RPi.GPIO as GPIO


# Set up stepper-motor:
GPIO.setmode(GPIO.BOARD)
motor = Motor([18,22,24,26])
angle =90

motor.move_to(angle)
sleep (4)
#motor.move_to(angle)



