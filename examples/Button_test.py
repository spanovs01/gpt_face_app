#!/usr/bin/env python3
import sys
import os
import time
import RPi.GPIO as GPIO
   
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
result = 0

while True:
    if GPIO.input(17) == True:
        os.system("espeak -ven-m1 -a50 'Reset'")
        time.sleep(1)
        if GPIO.input(17) == True:
            time.sleep(1)
            if GPIO.input(17) == True:
                os.system("espeak -ven-m1 -a50 'Shut down'")
                result = 1
        
        break
    time.sleep(1)

GPIO.cleanup()
if result == 0:
    print('System Reset')
    os.system("sudo shutdown --reboot now")
else:
    print('System shuts down')
    os.system("sudo shutdown --poweroff now")



