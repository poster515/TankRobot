#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

#Definition of ultrasonic module pins
EchoPin = 0
TrigPin = 1

#Definition of RGB module pins
LED_R = 22
LED_G = 27
LED_B = 24

#Definition of servo pin
Servo_sensor = 23
Servo_cam_x_y = 11
Servo_cam_z = 9

def servo_test(pin: int = 23):
    Servo_sensor = pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(Servo_sensor, GPIO.OUT)
    p = GPIO.PWM(Servo_sensor, 50) # 50 Hz PWM signal
    p.start(2.5) # Initialization
    try:
        while True:
            p.ChangeDutyCycle(5)
            time.sleep(0.5)
            p.ChangeDutyCycle(7.5)
            time.sleep(0.5)
            p.ChangeDutyCycle(10)
            time.sleep(0.5)
            p.ChangeDutyCycle(12.5)
            time.sleep(0.5)
            p.ChangeDutyCycle(10)
            time.sleep(0.5)
            p.ChangeDutyCycle(7.5)
            time.sleep(0.5)
            p.ChangeDutyCycle(5)
            time.sleep(0.5)
            p.ChangeDutyCycle(2.5)
            time.sleep(0.5)
    except KeyboardInterrupt:
        p.stop()
        GPIO.cleanup()

#Motor pins are initialized into output mode
#Key pin is initialized into input mode
#Ultrasonic pin,RGB pin,servo pin initialization
def init():

    #Set the GPIO port to BCM encoding mode
    GPIO.setmode(GPIO.BCM)

    #Ignore warning information
    GPIO.setwarnings(False)

    global pwm_servo_sensor
    global pwm_servo_cam_x_y
    global pwm_servo_cam_z
    GPIO.setup(EchoPin,GPIO.IN)
    GPIO.setup(TrigPin,GPIO.OUT)
    GPIO.setup(LED_R, GPIO.OUT)
    GPIO.setup(LED_G, GPIO.OUT)
    GPIO.setup(LED_B, GPIO.OUT)
    GPIO.setup(Servo_sensor, GPIO.OUT)
    GPIO.setup(Servo_cam_x_y, GPIO.OUT)
    GPIO.setup(Servo_cam_z, GPIO.OUT)

    pwm_servo_sensor = GPIO.PWM(Servo_sensor, 50) # 50 Hz PWM signal
    pwm_servo_cam_x_y = GPIO.PWM(Servo_cam_x_y, 50)
    pwm_servo_cam_z = GPIO.PWM(Servo_cam_z, 50)
    pwm_servo_sensor.start(0) # start PWM of with Duty Cycle 0 (i.e., off)
    pwm_servo_cam_x_y.start(0)
    pwm_servo_cam_z.start(0)

#Ultrasonic function
'''
def Distance_test():
    GPIO.output(TrigPin,GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TrigPin,GPIO.LOW)
    while not GPIO.input(EchoPin):
        pass
    t1 = time.time()
    while GPIO.input(EchoPin):
        pass
    t2 = time.time()
    print "distance is %d " % (((t2 - t1)* 340 / 2) * 100)
    time.sleep(0.01)
    return ((t2 - t1)* 340 / 2) * 100
'''
def Distance():
    GPIO.output(TrigPin,GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin,GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(TrigPin,GPIO.LOW)

    t3 = time.time()

    while not GPIO.input(EchoPin):
        if (time.time() - t3) > 0.03:
            return -1

    t1 = time.time()

    while GPIO.input(EchoPin):
        if(time.time() - t1) > 0.03:
            return -1

    t2 = time.time()
    time.sleep(0.01)
    distance = (((t2 - t1)* 340 / 2) * 100) / 2.54
    print("distance is {0:3.2f} in".format(distance))
    return distance

def Distance_test():
    num = 0
    ultrasonic = []
    while num < 5:
        distance = Distance()
        while int(distance) == -1 :
            distance = Distance()
            print("Tdistance is {}".format(distance) )
        while (int(distance) >= 500 or int(distance) == 0) :
            distance = Distance()
            print("Edistance is {}".format(distance) )
        ultrasonic.append(distance)
        num = num + 1
        time.sleep(0.01)
    print(ultrasonic)
    distance = (ultrasonic[1] + ultrasonic[2] + ultrasonic[3])/3
    print("distance is {}".format(distance))
    return distance

#The servo rotates to the specified angle
def servo_move(servo_pwm, pos):
    """
    Take an angle between -90 and +90 and move the servo to that angle.
    """
    # 0.5ms-----------------0°
    # 1.0ms-----------------45°
    # 1.5ms-----------------90°
    # 2.0ms-----------------135°
    # 2.5ms-----------------180°
    servo_pwm.ChangeDutyCycle(pos/90 + 0.5)

def servo_color_carstate(color):

    if color == "RED":
        #Magenta
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.LOW)
    elif color == "BLUE":
        #Blue
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
    elif color == "GREEN":
        #Green
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.HIGH)
        GPIO.output(LED_B, GPIO.LOW)

def stop():
    pwm_servo_sensor.stop()
    pwm_servo_cam_x_y.stop()
    pwm_servo_cam_z.stop()
    GPIO.cleanup()
