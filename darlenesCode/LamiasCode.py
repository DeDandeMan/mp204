#sudo apt-get install espeak -y
#cd ~/raphael-kit/python/
#python3 3.1.4_Text-to-speech.py




#from tts import TTS


def detect_object_direction():
    return "front"  # Placeholder value


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


def main():
    tts = TTS(engine="espeak")
    tts.lang('en-US')


    vibrator_motor_level = 3  # Placeholder value for motor level


    # Assuming vibrator_motor_level indicates high-speed approaching objects
    if vibrator_motor_level == 3:
        object_direction = detect_object_direction()
        alert_message = get_alert_message(object_direction)
        print(alert_message)
        tts.say(alert_message)


def destroy():
    tts.say('See you later')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()



