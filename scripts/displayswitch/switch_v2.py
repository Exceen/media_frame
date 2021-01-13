#!/usr/bin/python2
import RPi.GPIO as GPIO
import time

display = 27
#display = 13

#GPIO.setmode(GPIO.BOARD)
GPIO.setmode(GPIO.BCM)
GPIO.setup(display, GPIO.OUT, initial=GPIO.HIGH)
GPIO.output(display, GPIO.LOW)
time.sleep(0.2)
GPIO.output(display, GPIO.HIGH)

#time.sleep(60)


GPIO.cleanup()


