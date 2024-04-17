#!/usr/bin/env python3
#version 14

import smbus2 as smbus  #used by the Gyro
import math             #used by the Gyro
import time             #used by everything
import RPi.GPIO as GPIO #used by the Ultrasonic sensor and Vibration motor
import subprocess       #used by text to speech

#UltraSonic Sensors GPIO slots - the value is the number for the software side, the commented out number is the GPIO slot number.
FRONTTRIG = 11 #17
FRONTECHO = 12 #18
BACKTRIG = 37 #26
BACKECHO = 38 #20
LEFTTRIG = 35 #19
LEFTECHO = 36 #16
RIGHTTRIG = 15 #22
RIGHTECHO = 16 #23

# Vibration Motors Pins - the value is the number for the software side, the commented out number is the GPIO slot number.
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

# The code to close out the RAM and other stuff being used by this code
def destroy():
   print("Exiting...")
   vmdestroy(FrontVM)
   vmdestroy(BackVM)
   vmdestroy(LeftVM)
   vmdestroy(RightVM)
   GPIO.cleanup()
   print("Exited successfully")

# ----------  Code for Ultrasonic Sensors  ----------

# This will setup the ultra sonic sensors
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

# getDistance() gets the distance as obtained by an ultrasonic sensor
# TRIG - the trig value for the sensor to get the distance from
# ECHO - the echo value for the sensor to get the distance from
# returns the distance in cm
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

#---------  code for the vibration Motors  ----------

#setupBuzzer() tells the raspberry pi how to communicate with the passed in Vibration Motor
def setupBuzzer(pin):
   GPIO.setmode(GPIO.BOARD)       
   GPIO.setup(pin, GPIO.OUT)
   GPIO.output(pin, GPIO.LOW)

# Clears the space the Vibration Motors used for other things 
def vmdestroy(vm):
   GPIO.output(vm, GPIO.LOW)
  
# Turns the Vibration Motor on
def vmOn(vm):
   GPIO.output(vm, GPIO.HIGH)

# Turns the Vibration Motor off
def vmOff(vm):
   GPIO.output(vm, GPIO.LOW)

# outputs the text-to-speech of the passed in text
def speak(text):
	subprocess.run(["espeak", text])

# turns the Vibration Motor off and on
def VMbeep(vm, x):
	while x > 0:
		vmOn(vm)
		time.sleep(.25)
		vmOff(vm)
		time.sleep(.25)
		x -= 1

# ----------  Code for the Gyro  ----------

# Gyro setup code
bus = smbus.SMBus(1)
address = 0x68 
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

# ----------  360 Hat code  ----------

# calcLevel() takes a distance and a speed and returns a danger level from 0 to 3
def calcLevel(distance, speed):
	if (speed < 72.860686 and speed > 5) and distance < 200:
		return 1
	elif (speed < 129.078084 and speed >= 72.860686) and (distance < 400 and distance > 200):
		return 2
	elif speed >= 129.078084 and distance < 1000:
		return 3
	else:
		return 0

# doOutput() manages the outputs according to the inputs
# sideDist - the distance of side 's'
# SpeedS - the speed of side 's'
# testGyro - the value of whether the gyro has turned significantly
# SideVM - the corresponding Vibration Motor to side 's'
# speak_message - the text that will get sent to the text to speech if danger level is high enough#
def doOutput(sideDist, SpeedS, testGyro, SideVM, speak_message):
	if((abs(SpeedS >= 1)) and testGyro):
		if  ((calcLevel(sideDist, SpeedS)== 1) or (sideDist > 400 and sideDist < 800)):
			VMbeep(SideVM, 1)
			return
		if  ((calcLevel(sideDist, SpeedS) == 2) or (sideDist > 200 and sideDist < 400)):
			VMbeep(SideVM, 2)
			return
		if  ((calcLevel(sideDist, SpeedS) == 3) or (sideDist < 200)):
			speak(speak_message)
			VMbeep(SideVM, 3)

# returns 0 if round one, then returns speed for each following round
def getSpeed(rounds, side):
	global distances
	global toutputs
	speed = 0
	if(rounds > 1):
		speed = (distances[side][-1] - distances[side][-2])/(toutputs[side][-1] - toutputs[side][-2])
	return speed

# prints to the terminal the distance and the speed
def printLine(strSide, dis, speed): 
	print(strSide, 'Distance: ', dis, 'cm', 'Speed: ', speed, 'cm/sec')

rounds = 0
distances = [[],[],[],[]]
toutputs = [[],[],[],[]]
gyros = [[],[],[]]

#Main body of code that will repeat as long as the hat is on
def loop():
	global rounds
	testGyro = True
	speedF = speedB = speedL = speedR = 0
	global toutputs  # Front, Back, Left, Right
	global distances   # Front, Back, Left, Right
	usf = 0
	usb = 1
	usl = 2
	usr = 3
	global gyros
	gx = 0
	gy =1
	gz = 2

	while True:  #continuously Repeating code
		rounds = 1 + rounds
		print("\nRound: ", rounds)
		sleepLength = .25
	   	   
		frontDistance = getDistance(FRONTTRIG, FRONTECHO)
		distances[usf].append(frontDistance)
		toutputs[usf].append(time.time())
		speedF = getSpeed(rounds,0)
		printLine('Front', frontDistance,speedF)
		doOutput(frontDistance, speedF, testGyro, FrontVM, f"Watch your Front")
		time.sleep(sleepLength)
	   
		backDistance = getDistance(BACKTRIG, BACKECHO)
		distances[usb].append(backDistance)
		toutputs[usb].append(time.time())
		speedB = getSpeed(rounds,1)
		printLine('Back',backDistance,speedB)
		doOutput(backDistance, speedB, testGyro, BackVM, f"Behind you")
		time.sleep(sleepLength)
		  
		leftDistance = getDistance(LEFTTRIG, LEFTECHO)
		distances[usl].append(leftDistance)
		toutputs[usl].append(time.time())
		speedL = getSpeed(rounds,2)
		printLine('Left', leftDistance,speedL)
		doOutput(leftDistance, speedL, testGyro, LeftVM, f"On your left")
		time.sleep(sleepLength)
		  
		rightDistance = getDistance(RIGHTTRIG, RIGHTECHO)
		distances[usr].append(rightDistance)
		toutputs[usr].append(time.time())
		speedR = getSpeed(rounds,3)
		printLine('Right',rightDistance,speedR)
		doOutput(rightDistance, speedR, testGyro, RightVM, f"On your right")
		time.sleep(sleepLength)
	   	  
		
	   
		gyro_xout = read_word_2c(0x43)
		gyro_yout = read_word_2c(0x45)
		gyro_zout = read_word_2c(0x47)
	  
		gyros[gx].append(gyro_xout / 131)
		gyros[gy].append(gyro_yout / 131)
		gyros[gz].append(gyro_zout / 131)
	   
		#print("xGyro value: ", gyros[gx][-1])
		#print("yGyro value: ", gyros[gy][-1])
		print("zGyro value: ", gyros[gz][-1])
		print("")

		
	   
		if rounds > 1:
			deltaX = abs(gyros[gx][-2]) - (gyros[gx][-1])
			deltaY = abs(gyros[gy][-2]) - (gyros[gy][-1])
			deltaZ = abs(gyros[gz][-2]) - (gyros[gz][-1])

			#print("DeltaX value: ", deltaX)
			#print("DeltaY value: ", deltaY)
			print("DeltaZ value: ", deltaZ)
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
