def gyroSpin():
    return 3

def getDanger():
    if gyroSpin() > 5:
        dangerLevel = 0
    elif gyroSpin () > 3:
        dangerLevel = 1
    elif gyroSpin() == 0:
        dangerLevel = 0