#!/usr/bin/env python3


import smbus2 as smbus  #used by the Gyro
import math             #used by the Gyro
import time             #used by everything
import RPi.GPIO as GPIO #used by the Ultrasonic sensor and Vibration motor
#from tts import TTS


#UltraSonic Sensors GPIO slots
FRONTTRIG = 11 #17
FRONTECHO = 12 #18
BACKTRIG = 37 #26
BACKECHO = 38 #20
LEFTTRIG = 35 #19
LEFTECHO = 36 #16
RIGHTTRIG = 15 #22
RIGHTECHO = 16 #23


# Vibration Motors Pins
FrontVM = 22 #25
BackVM = 29 #5
LeftVM = 40 #21
RightVM = 31 #6


# Gyro Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c


#General Setup/Destroy code
def setup():
   setupBuzzer(FrontVM)
   setupBuzzer(BackVM)
   setupBuzzer(LeftVM)
   setupBuzzer(RightVM)
   setupUltraSonicSensors()
   # the Gyro doesn't need a setup


def destroy():
   print("Exiting...")
   vmdestroy(FrontVM)
   vmdestroy(BackVM)
   vmdestroy(LeftVM)
   vmdestroy(RightVM)
   GPIO.cleanup()
   print("Exited successfully")

#Code for the headphones
def get_alert_message(direction):
    if direction == "front":
        return "Watch out in front!"
    elif direction == "left":
        return "On your left!"
    elif direction == "right":
        return "On your right!"
    elif direction == "behind":
        return "Behind you!"
    else:
        return " "
    
def mainHeadphones(direction, level):
    if level == 3:
        #object_direction = detect_object_direction()
        alert_message = get_alert_message(direction)
        print(alert_message)
        #tts.say(alert_message)

# Code for Ultrasonic Sensors
def setupUltraSonicSensors():
   GPIO.setmode(GPIO.BOARD)
   GPIO.setup(FRONTTRIG, GPIO.OUT)
   GPIO.setup(FRONTECHO, GPIO.IN)
   GPIO.setup(BACKTRIG, GPIO.OUT)
   GPIO.setup(BACKECHO, GPIO.IN)
   GPIO.setup(LEFTTRIG, GPIO.OUT)
   GPIO.setup(LEFTECHO, GPIO.IN)
   GPIO.setup(RIGHTTRIG, GPIO.OUT)
   GPIO.setup(RIGHTECHO, GPIO.IN)


def getDistance(TRIG, ECHO):
   GPIO.output(TRIG, 0)
   time.sleep(0.000002)


   GPIO.output(TRIG, 1)
   time.sleep(0.25)
   GPIO.output(TRIG, 0)


   while GPIO.input(ECHO) == 0:
       a = 0
   time1 = time.time()
   while GPIO.input(ECHO) == 1:
       a = 1
   time2 = time.time()


   during = time2 - time1
   return during * 340 / 2 * 100


#code for the vibration Motors
def setupBuzzer(pin):
   GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)


def vmdestroy(vm):
   GPIO.output(vm, GPIO.LOW)
  
def vmOn(vm):
   GPIO.output(vm, GPIO.HIGH)


def vmOff(vm):
   GPIO.output(vm, GPIO.LOW)


def VMbeep(vm, x):
   times = x
   while times > 0:
       vmOn(vm)
       time.sleep(.25)
       vmOff(vm)
       time.sleep(.25)
       times = times - 1


# Code for the Gyro
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command


# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)


def read_byte(adr):
   return bus.read_byte_data(address, adr)


def read_word(adr):
   high = bus.read_byte_data(address, adr)
   low = bus.read_byte_data(address, adr+1)
   val = (high << 8) + low
   return val


def read_word_2c(adr):
   val = read_word(adr)
   if (val >= 0x8000):
       return -((65535 - val) + 1)
   else:
       return val


def dist(a,b):
   return math.sqrt((a*a)+(b*b))


def get_y_rotation(x,y,z):
   radians = math.atan2(x, dist(y,z))
   return -math.degrees(radians)


def get_x_rotation(x,y,z):
   radians = math.atan2(y, dist(x,z))
   return math.degrees(radians)




def testGyro():
   # Initial array to store all values
   outputs = []
  
   while True:
       # time.sleep(0.1)
       gyro_xout = read_word_2c(0x43)
       gyro_yout = read_word_2c(0x45)
       gyro_zout = read_word_2c(0x47)


       accel_xout = read_word_2c(0x3b)
       accel_yout = read_word_2c(0x3d)
       accel_zout = read_word_2c(0x3f)


       accel_xout_scaled = accel_xout / 16384.0
       accel_yout_scaled = accel_yout / 16384.0
       accel_zout_scaled = accel_zout / 16384.0


       xgyro = (gyro_xout / 131)
       ygyro = (gyro_yout / 131)


       current = [xgyro, ygyro]
       outputs.append(current)
       time.sleep(0.25)
      
       if len(outputs) > 1:
           deltaX = abs(outputs[-1][0]) - (outputs[-2][0])
           deltaY = abs(outputs[-1][1]) - (outputs[-2][1])
           if (deltaX > 40) and (deltaY > 40):
               return False
           elif (deltaX > 30 and deltaX < 75) and (deltaY > 0 and deltaY < 15):
               return False
           else:
               return True
       else:
           return True


def testLoop():
   while True:
       print('ULTRASONIC SENSORS')
       FRONTdis = getDistance(FRONTTRIG, FRONTECHO)
       print ('FRONT', FRONTdis, 'cm')
       print ('')
       time.sleep(0.3)
       BACKdis = getDistance(BACKTRIG, BACKECHO)
       print ('BACK', BACKdis, 'cm')
       print ('')
       time.sleep(0.3)
       LEFTdis = getDistance(LEFTTRIG, LEFTECHO)
       print ('LEFT', LEFTdis, 'cm')
       print ('')
       time.sleep(0.3)
       RIGHTdis = getDistance(RIGHTTRIG, RIGHTECHO)
       print ('RIGHT', RIGHTdis, 'cm')
       print ('')
       time.sleep(0.3)


       VMbeep(FrontVM, 0.5)
       testGyro()


def calcLevel(distance, speed):
   if (speed < 72.860686 and speed > 15) and distance < 200:
       return "1"
   elif speed < 129.078084 and (distance < 400 and distance > 200):
       return "2"
   elif speed > 129.078084 and distance > 400:
       return "3"
   else:
       return "0"
   
def tryBeep(side, dis, speed):
    if  (calcLevel(dis, speed) == "1") and (testGyro() == True):
        VMbeep(side, 1)
    if  ((calcLevel(dis, speed) == "2") or (dis < 300 and dis > 200)) and (testGyro() == True):
        VMbeep(side, 3)
    if  ((calcLevel(dis, speed) == "3") or (dis < 200))  and (testGyro() == True):
        VMbeep(side, 5)
  
def loop():
    round = 0
    # Array to store values for US
    usoutputs = []
    last_time = time.time()
    speedF = speedB = speedL = speedR = 0
  
    while True:    
        round += 1
        print('')
        print("Round: ", round)
        print('')
      
        frontDistance = getDistance(FRONTTRIG, FRONTECHO)
        print ('FRONT', frontDistance, 'cm')
        tryBeep(FrontVM, frontDistance, speedF)
        time.sleep(.1)

        rightDistance = getDistance(RIGHTTRIG, RIGHTECHO)
        print ('RIGHT', rightDistance, 'cm')
        tryBeep(RightVM, rightDistance, speedR)
        time.sleep(.1)
      
        backDistance = getDistance(BACKTRIG, BACKECHO)
        print ('BACK', backDistance, 'cm')
        tryBeep(BackVM, backDistance, speedB)
        time.sleep(.1)
          
        leftDistance = getDistance(LEFTTRIG, LEFTECHO)
        print ('LEFT', leftDistance, 'cm')
        tryBeep(LeftVM, leftDistance, speedL)
        time.sleep(.1)


        current_time = time.time()
        time_diff = current_time - last_time
        uscurrent = [frontDistance, backDistance, leftDistance, rightDistance]
        usoutputs.append(uscurrent)
      
        if len(usoutputs) > 1:
           speedF = ((usoutputs[-1][0]) - (usoutputs[-2][0])) / time_diff
           speedB = ((usoutputs[-1][1]) - (usoutputs[-2][1])) / time_diff
           speedL = ((usoutputs[-1][2]) - (usoutputs[-2][2])) / time_diff
           speedR = ((usoutputs[-1][3]) - (usoutputs[-2][3])) / time_diff
          
        last_time = current_time
      
        print('Speed FRONT:', speedF, ' cm/s')
        print('Speed BACK:', speedB, ' cm/s')
        print('Speed LEFT:', speedL, ' cm/s')
        print('Speed RIGHT:', speedR, ' cm/s')


if __name__ == "__main__":
   setup()
   try:
       #testLoop()
       loop()
   except KeyboardInterrupt:
       destroy()
