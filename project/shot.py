import RPi.GPIO as GPIO
import time

def pour_shot():
    PUMP = 2 # IO2 is the fan aka pump output
    # pump is active low (i.e., turn low to turn on)
    GPIO.output(PUMP, GPIO.LOW)
    time.sleep(20) # seconds
    GPIO.output(PUMP, GPIO.HIGH)

def servo_move(servo_pwm, servo_pin, desired_pos):
    """
    Moves the provided servo to the desired position
    over the course of 1 second.
    """
    if 500 < float(desired_pos) < 2600:
        # account for a little wiggle in value
        # print("moving servo {} to position {}".format(servo_pwm, desired_pos))
        servo_pwm.set_servo_pulsewidth(servo_pin, float(desired_pos));
