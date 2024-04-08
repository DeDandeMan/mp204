import RPi.GPIO as GPIO
import time

#UltraSonic Sensors GPIO slots
FRONTTRIG = 11 #17
FRONTECHO = 12 #18
BACKTRIG = 37 #26
BACKECHO = 38 #20
LEFTTRIG = 35 #19
LEFTECHO = 36 #16
RIGHTTRIG = 15 #22
RIGHTECHO = 16 #23

def setup(trig, echo):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(FRONTTRIG, GPIO.OUT)
    GPIO.setup(FRONTECHO, GPIO.IN)
    GPIO.setup(BACKTRIG, GPIO.OUT)
    GPIO.setup(BACKECHO, GPIO.IN)
    GPIO.setup(LEFTTRIG, GPIO.OUT)
    GPIO.setup(LEFTECHO, GPIO.IN)
    GPIO.setup(RIGHTTRIG, GPIO.OUT)
    GPIO.setup(RIGHTECHO, GPIO.IN)

def getDistance(trig, echo):
    GPIO.output(trig, 0)
    time.sleep(0.000002)

    GPIO.output(trig, 1)
    time.sleep(0.25)
    GPIO.output(trig, 0)

    while GPIO.input(echo) == 0:
        a = 0
    time1 = time.time()
    while GPIO.input(echo) == 1:
        a = 1
    time2 = time.time()

    during = time2 - time1
    return during * 340 / 2 * 100
    
def getSpeed(dis1, dis2):
    return (dis2 - dis1)