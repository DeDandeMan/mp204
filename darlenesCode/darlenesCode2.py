#!/usr/bin/env python3


import smbus2 as smbus  #used by the Gyro
import math             #used by the Gyro
import time             #used by everything
import RPi.GPIO as GPIO #used by the Ultrasonic sensor and Vibration motor
import subprocess       #used by text to speech

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
   #print("Exiting...")
   vmdestroy(FrontVM)
   vmdestroy(BackVM)
   vmdestroy(LeftVM)
   vmdestroy(RightVM)
   GPIO.cleanup()
   #print("Exited successfully")


# Code for Ultrasonic Sensors
def setupUltraSonicSensors():
   #print("Setting up US Sensors")
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
   #print("getting distance")
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
   #print("Setting up buzzer")
   GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)


def vmdestroy(vm):
   GPIO.output(vm, GPIO.LOW)
  
def vmOn(vm):
   GPIO.output(vm, GPIO.HIGH)


def vmOff(vm):
   GPIO.output(vm, GPIO.LOW)

def speak(text):
	subprocess.run(["espeak", text])
	
def VMbeep(vm, x):
   #print('start method, VMBeep')
   while x > 0:
	   vmOn(vm)
	   time.sleep(.25)
	   vmOff(vm)
	   time.sleep(.25)
	   x -= 1


# Code for the Gyro
bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command


# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)


def read_byte(adr):
   #print('read_byte')
   return bus.read_byte_data(address, adr)


def read_word(adr):
   #print('read_word')
   high = bus.read_byte_data(address, adr)
   low = bus.read_byte_data(address, adr+1)
   val = (high << 8) + low
   return val


def read_word_2c(adr):
   #print('read_word')
   val = read_word(adr)
   if (val >= 0x8000): #TODO - What is this number
	   return -((65535 - val) + 1)
   else:
	   return val


def dist(a,b):
   #print('dist')
   return math.sqrt((a*a)+(b*b))


def get_y_rotation(x,y,z):
   #print('get_y_rotation')
   radians = math.atan2(x, dist(y,z))
   return -math.degrees(radians)


def get_x_rotation(x,y,z):
   #print('get_x_rotation')
   radians = math.atan2(y, dist(x,z))
   return math.degrees(radians)


def calcLevel(distance, speed):
   #print('calcLevel')
   if (speed < 72.860686 and speed > 5) and distance < 200:
	   return 1
   elif (speed < 129.078084 and speed >= 72.860686) and (distance < 400 and distance > 200):
	   return 2
   elif speed >= 129.078084 and distance < 1000:
	   return 3
   else:
	   return 0
  
def loop():
   round = 0
   usoutputs = []
   outputs = []
   speedF = speedB = speedL = speedR = 0
   timeF = timeB = timeL = timeR = 0
   testGyro = True
   toutputs = []
  
   while True:
	   round += 1
	   print('')
	   print("\nRound: ", round)
	   if round > 2:
	      print(testGyro)
	   
	   
	   frontDistance = getDistance(FRONTTRIG, FRONTECHO)
	   tflast = time.time()
	   if  ((calcLevel(frontDistance, speedF) == 1) or (frontDistance > 400 and frontDistance < 800)) and (testGyro):
		   VMbeep(FrontVM, 1)
	   if  ((calcLevel(frontDistance, speedF) == 2) or (frontDistance > 200 and frontDistance < 400)) and (testGyro):
		   VMbeep(FrontVM, 2)
	   if  ((calcLevel(frontDistance, speedF) == 3) or (frontDistance < 200)) and (testGyro):
		   VMbeep(FrontVM, 3)
		   speak_message = f"Watch your front"
		   speak(speak_message)
	   print("Front Speed: ", speedF, '\n')
	   print('\nFront time: ', timeF, '\n')
	   
	   
	   backDistance = getDistance(BACKTRIG, BACKECHO)
	   tblast = time.time()
	   print ('BACK', backDistance, 'cm')
	   if  ((calcLevel(backDistance, speedB) == 1) or (backDistance > 400 and backDistance < 800)) and (testGyro):
		   VMbeep(BackVM, 1)
	   if  ((calcLevel(backDistance, speedB) == 2) or (backDistance > 200 and backDistance < 400)) and (testGyro):
		   VMbeep(BackVM, 2)
	   if  ((calcLevel(backDistance, speedB) == 3) or (backDistance < 200)) and (testGyro):
		   VMbeep(BackVM, 3)
		   speak_message = f"Behind you"
		   speak(speak_message)
	   print('\nBack time: ', timeB, '\n')
		
		
	   leftDistance = getDistance(LEFTTRIG, LEFTECHO)
	   tllast = time.time()
	   print ('LEFT', leftDistance, 'cm')
	   if  ((calcLevel(leftDistance, speedL) == 1) or (leftDistance > 400 and leftDistance < 800)) and (testGyro):
		   VMbeep(LeftVM, 1)
	   if  ((calcLevel(leftDistance, speedL) == 2) or (leftDistance > 200 and leftDistance < 400)) and (testGyro):
		   VMbeep(LeftVM, 2)
	   if  ((calcLevel(leftDistance, speedL) == 3) or (leftDistance < 200)) and (testGyro):
		   VMbeep(LeftVM, 3)
		   speak_message = f"On your left"
		   speak(speak_message)
	   print('\nLeft time: ', timeL, '\n')
		
		
	   rightDistance = getDistance(RIGHTTRIG, RIGHTECHO)
	   trlast = time.time()
	   print ('RIGHT', rightDistance, 'cm')
	   if  ((calcLevel(rightDistance, speedR) == 1) or (rightDistance > 400 and rightDistance < 800)) and (testGyro):
		   VMbeep(RightVM, 1)
	   if  ((calcLevel(rightDistance, speedR) == 2) or (rightDistance > 200 and rightDistance < 400)) and (testGyro):
		   VMbeep(RightVM, 2)
	   if  ((calcLevel(rightDistance, speedR) == 3) or (rightDistance < 200)) and (testGyro):
		   VMbeep(RightVM, 3)
		   speak_message = f"On your right"
		   speak(speak_message)
	   print('\nRight time: ', timeR, '\n')
	   
	  
	   tlast = [tflast, tblast, tllast, trlast]
	   toutputs.append(tlast)
	   
	   if len(toutputs) > 1:
	      timeF = (toutputs[-1][0]) - (toutputs[-2][0])
	      timeB = (toutputs[-1][1]) - (toutputs[-2][1])
	      timeL = (toutputs[-1][2]) - (toutputs[-2][2])
	      timeR = (toutputs[-1][3]) - (toutputs[-2][3])

	   
	   uscurrent = [frontDistance, backDistance, leftDistance, rightDistance]
	   usoutputs.append(uscurrent)
	   	  
	   if len(usoutputs) > 1:
	      speedF = ((usoutputs[-2][0]) - (usoutputs[-1][0])) / timeF
	      speedB = ((usoutputs[-2][1]) - (usoutputs[-1][1])) / timeB
	      speedL = ((usoutputs[-2][2]) - (usoutputs[-1][2])) / timeL
	      speedR = ((usoutputs[-2][3]) - (usoutputs[-1][3])) / timeR
	  
	   print('Speed FRONT:', speedF, ' cm/s')
	   print('Speed BACK:', speedB, ' cm/s')
	   print('Speed LEFT:', speedL, ' cm/s')
	   print('Speed RIGHT:', speedR, ' cm/s')
	   
	   gyro_xout = read_word_2c(0x43)
	   gyro_yout = read_word_2c(0x45)
	  
	   xgyro = (gyro_xout / 131)
	   ygyro = (gyro_yout / 131)

	   current = [xgyro, ygyro]
	   outputs.append(current)
	   
	   print("\nxGyro value: ", xgyro)
	   print("yGyro value: ", ygyro)
	   print("\n")
	   
	   if len(outputs) > 1:
		   deltaX = abs(outputs[-2][0]) - (outputs[-1][0])
		   deltaY = abs(outputs[-2][1]) - (outputs[-1][1])
		   
		   print("\nDeltaX value: ", deltaX)
		   print("DeltaY value: ", deltaY)
		   print("\n")
		   
		   if (deltaX > 40) or (deltaY > 40):
			   testGyro = False
			   print("gyro in range")
		   elif (deltaX > 30 and deltaX < 75) or (deltaY > 0 and deltaY < 15):
			   testGyro = False
			   print("gyro in range")
		   else:
			   testGyro = True

if __name__ == "__main__":
   setup()
   try:
	   loop()
   except KeyboardInterrupt:
	   destroy()
