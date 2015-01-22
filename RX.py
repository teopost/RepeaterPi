import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
ANTENNA_SWITCH = 24
PTT = 26
GPIO.setup(ANTENNA_SWITCH, GPIO.OUT)
GPIO.setup(PTT, GPIO.OUT)

GPIO.output(PTT, GPIO.LOW)
time.sleep(.5)
GPIO.output(ANTENNA_SWITCH, GPIO.LOW)