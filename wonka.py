def getDistance():
    #get the distance from the Ultrasonic Sensor
    return 0

def getSpeed():
    #get the speed from the past two distances the ultrasonic sensor gathered
    speed = getDistance() + getDistance()
    return 0

def getDangerLevel():
    return getDistance() + getSpeed()

def output():
    getDangerLevel()

