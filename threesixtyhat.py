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
FrontVM = 7
BackVM = 29
LeftVM = 40
RightVM = 31

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

def VMbeep(vm, x):
	times = x
	while times > 0:
		vmOn(vm)
		time.sleep(x)
		vmOff(vm)
		time.sleep(x)
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
    time.sleep(0.1)
    gyro_xout = read_word_2c(0x43)
    gyro_yout = read_word_2c(0x45)
    gyro_zout = read_word_2c(0x47)

    print ("gyro_xout : ", gyro_xout, " scaled: ", (gyro_xout / 131))
    print ("gyro_yout : ", gyro_yout, " scaled: ", (gyro_yout / 131))
    print ("gyro_zout : ", gyro_zout, " scaled: ", (gyro_zout / 131))

    accel_xout = read_word_2c(0x3b)
    accel_yout = read_word_2c(0x3d)
    accel_zout = read_word_2c(0x3f)

    accel_xout_scaled = accel_xout / 16384.0
    accel_yout_scaled = accel_yout / 16384.0
    accel_zout_scaled = accel_zout / 16384.0

    print ("accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled)
    print ("accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled)
    print ("accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled)

    print ("x rotation: " , get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
    print ("y rotation: " , get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))

    time.sleep(0.5)

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

def loop():
	while True:
		print("Hello World!")
		if getDistance(FRONTTRIG, FRONTECHO) < 100:
			VMbeep(FrontVM, 3)
		if getDistance(BACKTRIG, BACKECHO) < 100:
			VMbeep(BackVM, 3)

if __name__ == "__main__":
	setup()
	try:
		#testLoop()
		loop()
	except KeyboardInterrupt:
		destroy()