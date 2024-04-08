import ultrasonicsensor as US

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

frontUS = US(FRONTTRIG, FRONTECHO)
print("FrontSensor", frontUS.getDistance())