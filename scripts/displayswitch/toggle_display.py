#!/usr/bin/python2
import RPi.GPIO as GPIO
import time
import argparse

switch = 27
led = 13

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led, GPIO.IN)
    GPIO.setup(switch, GPIO.OUT, initial=GPIO.HIGH)

def toggle():
    GPIO.output(switch, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(switch, GPIO.HIGH)

def is_display_on():
    return GPIO.input(led)

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--on', action='store_true', help='toggle on')
    parser.add_argument('--off', action='store_true', help='toggle off')
    args = parser.parse_args()

    if args.on == args.off:
        print 'Arguments error!'
        quit()

    setup_gpio()

    if args.on and not is_display_on():
        toggle()
        print 'turning on'
    elif args.off and is_display_on():
        toggle()
        print 'turning off'
    else:
        print 'doing nothing'

    GPIO.cleanup()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

