import RPi.GPIO as GPIO
import time

def pour_shot():
    PUMP = 2 # IO2 is the fan aka pump output
    # pump is active low (i.e., turn low to turn on)
    GPIO.output(PUMP, GPIO.LOW)
    time.sleep(3) # seconds
    GPIO.output(PUMP, GPIO.HIGH)