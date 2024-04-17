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