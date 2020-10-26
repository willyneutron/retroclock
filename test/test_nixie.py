import sys
sys.path.append('../MCP23017/')

import busio
import board
import time
import signal

import RPi.GPIO as GPIO
from datetime import datetime
from MCP23017_Nixie import MCP23017_Nixie_DigitController

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT, initial=GPIO.HIGH)

# Signal handler
def signal_handler(sig, frame):
    GPIO.setup(23, GPIO.OUT, initial=GPIO.LOW)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Digit controllers
i2c = busio.I2C(board.SCL, board.SDA)
digits = [0x9, 0x0, 0x1, 0x2, 0x3, 0x4, 0x5, 0x6, 0x7, 0x8]
digit_controller_a = MCP23017_Nixie_DigitController(i2c, digits, addr=0x20)
digit_controller_b = MCP23017_Nixie_DigitController(i2c, digits, addr=0x21)

digit_controller_a.connect()
digit_controller_b.connect()

def print_time (digit_controller_a, digit_controller_b):
    now = datetime.now()
    digit_controller_a.dot1 = now.second % 2
    digit_controller_a.dot2 = now.second % 2
    digit_controller_b.dot1 = now.second % 2
    digit_controller_b.dot2 = now.second % 2
    digit_controller_a.ms_digit = int(now.hour / 10)
    digit_controller_a.m_digit = int(now.hour % 10)
    digit_controller_a.ls_digit = int(now.minute / 10)
    digit_controller_b.ms_digit = int(now.minute % 10)
    digit_controller_b.m_digit = int(now.second / 10)
    digit_controller_b.ls_digit = int(now.second % 10)

print_time (digit_controller_a, digit_controller_b)

while True:
    time.sleep(1)
    print_time (digit_controller_a, digit_controller_b)
