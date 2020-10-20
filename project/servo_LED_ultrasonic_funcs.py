#-*- coding:UTF-8 -*-
import RPi.GPIO as GPIO
import time

#Definition of  ultrasonic module pins
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
    GPIO.setup(key,GPIO.IN)
    GPIO.setup(EchoPin,GPIO.IN)
    GPIO.setup(TrigPin,GPIO.OUT)
    GPIO.setup(LED_R, GPIO.OUT)
    GPIO.setup(LED_G, GPIO.OUT)
    GPIO.setup(LED_B, GPIO.OUT)
    GPIO.setup(Servo_sensor, GPIO.OUT)
    GPIO.setup(Servo_sensor, GPIO.OUT)
    GPIO.setup(Servo_sensor, GPIO.OUT)

    pwm_servo_sensor = GPIO.PWM(ServoPin, 50)
    pwm_servo_cam_x_y = GPIO.PWM(ServoPin, 50)
    pwm_servo_cam_z = GPIO.PWM(ServoPin, 50)
    pwm_servo_sensor.start(0)
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
    print("distance is {}".format(((t2 - t1)* 340 / 2) * 100))
    return ((t2 - t1)* 340 / 2) * 100

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
    print ultrasonic
    distance = (ultrasonic[1] + ultrasonic[2] + ultrasonic[3])/3
    print("distance is {}".format(distance) )
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

def servo_color_carstate():

    init()
    back(20, 20)
    time.sleep(0.08)
    brake()

    servo_appointed_detection(0)
    time.sleep(0.8)
    rightdistance = Distance_test()

    servo_appointed_detection(180)
    time.sleep(0.8)
    leftdistance = Distance_test()

    servo_appointed_detection(90)
    time.sleep(0.8)
    frontdistance = Distance_test()

    if leftdistance < 30 and rightdistance < 30 and frontdistance < 30:
        #Magenta
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
        spin_right(85, 85)
        time.sleep(0.58)
    elif leftdistance >= rightdistance:
        #Blue
        GPIO.output(LED_R, GPIO.LOW)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
    	spin_left(85, 85
        time.sleep(0.28)
    elif leftdistance <= rightdistance:
        #Magenta
        GPIO.output(LED_R, GPIO.HIGH)
        GPIO.output(LED_G, GPIO.LOW)
        GPIO.output(LED_B, GPIO.HIGH)
        spin_right(85, 85)
        time.sleep(0.28)

def stop():
    pwm_servo_sensor.stop()
    pwm_servo_cam_x_y.stop()
    pwm_servo_cam_z.stop()
    GPIO.cleanup()
