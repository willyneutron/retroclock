import sys
sys.path.append('../MCP23017/')

import signal
import busio
import board
import time
import string

from datetime import datetime
from MCP23017_HPDL_1414 import MCP23017_HPDL_1414_CharacterController

i2c = busio.I2C(board.SCL, board.SDA)
co = MCP23017_HPDL_1414_CharacterController(i2c, 0x23)
co.connect()

co.viewport = [
    (0,3), (0,2), (0,1), (0,0),
    (1,3), (1,2), (1,1), (1,0),
    (2,3), (2,2), (2,1), (2,0),
    (3,3), (3,2), (3,1), (3,0)
]

# Signal handler
def signal_handler(sig, frame):
    co.blank_viewport()
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

co.text = datetime.now().strftime("%A %d %B, %Y  ").upper()
while True:
    co.print_text()
    co.viewport_pos += 1
    time.sleep(0.5)

