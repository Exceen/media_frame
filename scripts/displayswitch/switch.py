#!/usr/bin/python2
import RPi.GPIO as GPIO
import time

display = 27
#display = 13

#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(display, GPIO.OUT)
GPIO.output(display, True)
time.sleep(0.2)
GPIO.output(display, False)

GPIO.cleanup()


