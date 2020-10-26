# -*- coding: utf-8 -*-
"""
    MCP23017 controller for К155ИД1 controlled 9-digit nixie tubes
 
	Under MIT License
    Copyright (c) 2020 Guillermo Climent, https://github.com/willyneutron
 
	Permission is hereby granted, free of charge, to any person obtaining a copy of this software
	and associated documentation files (the “Software”), to deal in the Software without restriction,
	including without limitation the rights to use, copy, modify, merge, publish, distribute,
	sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:
	The above copyright notice and this permission notice shall be included in all copies or 
	substantial portions of the Software.
	THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT 
	NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
	IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
	WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
	SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from adafruit_mcp230xx.mcp23017 import MCP23017, _MCP23017_ADDRESS

class MCP23017_Nixie_DigitController:

    def __init__(self, i2c, digits= [0x0, 0x9, 0x8, 0x7, 0x6, 0x5, 0x4, 0x3, 0x2, 0x1], addr=_MCP23017_ADDRESS):

        # Store config
        self._i2c = i2c
        self._addr = addr

        # Map containing the values for each digit
        #          0    1    2    3    4    5    6    7    8    9
        self._digits = digits

        # Base offsets for each of the 3 digits
        self._ms_digit_offset =     0
        self._m_digit_offset =      12
        self._ls_digit_offset =     8
        self._dot1_offset =         4
        self._dot2_offset =         5
        
        self._ms_digit = 0
        self._m_digit = 0
        self._ls_digit = 0
        self._dot1 = 0
        self._dot2 = 0

    def connect(self):
        # Connect to MCP device
        self._mcp = MCP23017(self._i2c, address=self._addr)
        
        # Set all GPIO as output and set it to 0
        if self._mcp != None:
            self._mcp.iodir = 0x00
            self._mcp.gpio = 0

        return self._mcp == None

    def _update(self):

        buffer = 0x00
        buffer |= self._digits[self._ms_digit] << self._ms_digit_offset
        buffer |= self._digits[self._m_digit] << self._m_digit_offset
        buffer |= self._digits[self._ls_digit] << self._ls_digit_offset
        buffer |= self._dot1 << self._dot1_offset
        buffer |= self._dot2 << self._dot2_offset

        self._mcp.gpio = buffer

    @property
    def ms_digit(self):
        return self._ms_digit

    @ms_digit.setter
    def ms_digit(self, val):
        self._ms_digit = val
        self._update()

    @property
    def m_digit(self):
        return self._m_digit

    @m_digit.setter
    def m_digit(self, val):
        self._m_digit = val
        self._update()        

    @property
    def ls_digit(self):
        return self._ls_digit

    @ls_digit.setter
    def ls_digit(self, val):
        self._ls_digit = val
        self._update()

    @property
    def dot1(self):
        return self._dot1

    @dot1.setter
    def dot1(self, val):
        self._dot1 = val
        self._update()

    @property
    def dot2(self):
        return self._dot2

    @dot2.setter
    def dot2(self, val):
        self._dot2 = val
        self._update()    
