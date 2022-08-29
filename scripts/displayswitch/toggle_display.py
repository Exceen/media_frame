#!/usr/bin/python3
import RPi.GPIO as GPIO
import time
import argparse
from os import path
from os import popen
from os import system
from subprocess import DEVNULL, STDOUT, call, Popen, PIPE

import asyncio
from kasa import SmartPlug

switch = 27
led = 13

WITH_DISCOVERYING = False # throws a lot of errors, still seems to work though...
FAKE_DISCOVERED_HOST_IP = '192.168.0.129'

config_path = path.dirname(path.realpath(__file__)) + '/display.config'

async def toggle_plug(status, plug):
    await plug.update()
    if status == 'on':
        await plug.turn_on()
    elif status == 'off':
        await plug.turn_off()

def set_power(status):
    if WITH_DISCOVERYING:
        host_command = "/home/pi/.local/bin/kasa --type plug discover | head -4 | grep -Eo '192.168.[0-9.]{2,}'"
        host_ip = popen(host_command).read().strip()
    else:
        host_ip = FAKE_DISCOVERED_HOST_IP
    
    p = SmartPlug(host_ip)
    asyncio.run(toggle_plug(status, p))

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led, GPIO.IN)
    GPIO.setup(switch, GPIO.OUT, initial=GPIO.HIGH)

def toggle():
    GPIO.output(switch, GPIO.LOW)
    time.sleep(0.2)
    GPIO.output(switch, GPIO.HIGH)

def set_config_status(status):
    config_status = 'status=' + status
    print('setting config status to ' + status)
    with open(config_path, 'w') as writer:
        writer.write(config_status)

def is_display_on():
    return GPIO.input(led)

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--on', action='store_true', help='toggle on')
    parser.add_argument('--off', action='store_true', help='toggle off')
    args = parser.parse_args()

    if not args.on and not args.off:
        if path.isfile(config_path):
            with open(config_path) as f:
                status = f.readline().split('=')[-1].strip()
                if status == 'on':
                    args.on = True
                elif status == 'off':
                    args.off = True

    if args.on == args.off:
        print('Arguments error!')
        quit()

    setup_gpio()

    print(is_display_on())

    did_something = False
    if args.on:
        set_config_status('on')
        if not is_display_on():
            set_power('on')
            time.sleep(3)
            toggle()
            did_something = True
            log('turning on')
    elif args.off:
        set_config_status('off')
        if is_display_on():
            toggle()
            time.sleep(3)
            set_power('off')
            did_something = True
            log('turning off')
    #else:
#    if not did_something:
#        log('doing nothing')

    GPIO.cleanup()

def log(message):
    print(message)

    with open('/home/pi/logs.txt', 'a') as f:
        f.write(time.strftime("%Y%m%d-%H%M%S"))
        f.write(' ' + message + '\n')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
