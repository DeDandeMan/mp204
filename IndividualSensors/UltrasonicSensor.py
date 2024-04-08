#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

FRONTTRIG = 11 #17
FRONTECHO = 12 #18
BACKTRIG = 37 #26
BACKECHO = 38 #20
LEFTTRIG = 35 #19
LEFTECHO = 36 #16
RIGHTTRIG = 15 #22
RIGHTECHO = 16 #23

def setup():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(FRONTTRIG, GPIO.OUT)
	GPIO.setup(FRONTECHO, GPIO.IN)
	GPIO.setup(BACKTRIG, GPIO.OUT)
	GPIO.setup(BACKECHO, GPIO.IN)
	GPIO.setup(LEFTTRIG, GPIO.OUT)
	GPIO.setup(LEFTECHO, GPIO.IN)
	GPIO.setup(RIGHTTRIG, GPIO.OUT)
	GPIO.setup(RIGHTECHO, GPIO.IN)

def distance(TRIG, ECHO):
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

def loop():
	while True:
		FRONTdis = distance(FRONTTRIG, FRONTECHO)
		print ('FRONT',FRONTdis, 'cm')
		print ('')
		time.sleep(0.3)
		BACKdis = distance(BACKTRIG, BACKECHO)
		print ('BACK', BACKdis, 'cm')
		print ('')
		time.sleep(0.3)
		LEFTdis = distance(LEFTTRIG, LEFTECHO)
		print ('LEFT', LEFTdis, 'cm')
		print ('')
		time.sleep(0.3)
		RIGHTdis = distance(RIGHTTRIG, RIGHTECHO)
		print ('RIGHT', RIGHTdis, 'cm')
		print ('')
		time.sleep(0.3)

def destroy():
	GPIO.cleanup()

if __name__ == "__main__":
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		destroy()
		
