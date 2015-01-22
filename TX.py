import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
ANTENNA_SWITCH = 24
PTT = 26
GPIO.setup(ANTENNA_SWITCH, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(PTT, GPIO.OUT,initial=GPIO.LOW)

GPIO.output(ANTENNA_SWITCH, GPIO.HIGH)
time.sleep(.5)
GPIO.output(PTT, GPIO.HIGH)