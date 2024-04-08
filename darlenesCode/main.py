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
   print("Exiting...")
   vmdestroy(FrontVM)
   vmdestroy(BackVM)
   vmdestroy(LeftVM)
   vmdestroy(RightVM)
   GPIO.cleanup()
   print("Exited successfully")


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

def speak(text):
	subprocess.run(["espeak", text])
	
def VMbeep(vm, x):
	while x > 0:
		vmOn(vm)
		time.sleep(1)
		vmOff(vm)
		time.sleep(1)
		x -= 1


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

def calcLevel(distance, speed):
	if (speed < 72.860686 and speed > 5) and distance < 200:
		return 1
	elif (speed < 129.078084 and speed >= 72.860686) and (distance < 400 and distance > 200):
		return 2
	elif speed >= 129.078084 and distance < 1000:
		return 3
	else:
		return 0

toutputs = []
def testDanger(sideDist, SpeedS, testGyro, SideVM, speak_message):
	if  ((calcLevel(sideDist, SpeedS)== 1) or (sideDist > 400 and sideDist < 800)) and (testGyro):
		VMbeep(SideVM, 1)
	if  ((calcLevel(sideDist, SpeedS) == 2) or (sideDist > 200 and sideDist < 400)) and (testGyro):
		VMbeep(SideVM, 2)
	if  ((calcLevel(sideDist, SpeedS) == 3) or (sideDist < 200)) and (testGyro):
		VMbeep(SideVM, 3)
		speak(speak_message)
	toutputs.append(time.time())
	
def getSpeed(round, side):
	speed = 0
	if(round > 1):
		speed = (distances[side][-1] - distances[side][-2])/(toutputs[side][-1] - toutputs[side][-2])
	return speed

def printLine(strSide, dis, speed):
	print (strSide, 'Distance: ', dis, 'cm', strSide, 'Speed: ', speed, 'cm/sec')

distances = [[],[],[],[]]   # Front, Back, Left, Right
def loop():
	round = 0
	usoutputs = []                          #Array to store values for US
	
	speedF = speedB = speedL = speedR = 0
	testGyro = True
	toutputs = [[],[],[],[]]  # Front, Back, Left, Right

	while True:
		round += 1
		print('')
		print("\nRound: ", round)
	   	   
		frontDistance = getDistance(FRONTTRIG, FRONTECHO)
		distances[0].append(frontDistance)
		toutputs[0].append(time.time())
		speedF = getSpeed(round,0)
		printLine('Front', frontDistance,speedF)
		#print ('FRONT DISTANCE: ', frontDistance, 'cm','Front speed',speedF,'cm/s')
		testDanger(frontDistance, speedF, testGyro, FrontVM, f"Watch your Front")
		time.sleep(0.25)
	   
		backDistance = getDistance(BACKTRIG, BACKECHO)
		distances[1].append(backDistance)
		toutputs[1].append(time.time())
		speedB = getSpeed(round,1)
		printLine('Back',backDistance,speedB)
		#print ('BACK Distance', backDistance, 'cm')
		testDanger(backDistance, speedB, testGyro, FrontVM, f"Behind you")
		time.sleep(0.25)
		  
		leftDistance = getDistance(LEFTTRIG, LEFTECHO)
		distances[2].append(leftDistance)
		toutputs[2].append(time.time())
		speedL = getSpeed(round,2)
		printLine('Left', backDistance,speedB)
		#print ('LEFT', leftDistance, 'cm')
		testDanger(leftDistance, speedL, testGyro, BackVM, f"On your left")
		time.sleep(0.25)
		  
		rightDistance = getDistance(RIGHTTRIG, RIGHTECHO)
		distances[3].append(rightDistance)
		toutputs[3].append(time.time())
		speedR = getSpeed(round,3)
		printLine('Right',rightDistance,speedR)
		#print ('RIGHT', rightDistance, 'cm')
		testDanger(rightDistance, speedR, testGyro, RightVM, f"On your right")
		time.sleep(0.25)
	   
	  
		current_time = time.time()
		time_diff = (current_time - last_time)
		uscurrent = [frontDistance, backDistance, leftDistance, rightDistance] #------
		usoutputs.append(uscurrent)
	   	  
		
	   
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
