# -*- coding: utf-8 -*-
"""
    MCP23017 controller for HPDL_1414 LED Bubble screens
 
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

class MCP23017_HPDL_1414_CharacterController:

    def __init__(self, i2c, addr=_MCP23017_ADDRESS):

        # Store config
        self._i2c = i2c
        self._addr = addr

        # Map containing the values for each digit
        self._character = {
	    ' ': 0x20, '!': 0x21, '"': 0x22, '#': 0x23, '$': 0x24, '%': 0x25, '&': 0x26, '\'': 0x27, 
            '<': 0x28, '>': 0x29, '*': 0x2A, '+': 0x2B, ',': 0x2C, '-': 0x2D, '.': 0x2E, '/': 0x2F,
            '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34, '5': 0x35, '6': 0x36, '7': 0x37, 
            '8': 0x38, '9': 0x39, ':': 0x3A, ';': 0x3B, '<': 0x3C, '=': 0x3D, '>': 0x3E, '?': 0x3F,
            '@': 0x40, 'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45, 'F': 0x46, 'G': 0x47, 
            'H': 0x48, 'I': 0x49, 'J': 0x4A, 'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E, 'O': 0x4F,
	    'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54, 'U': 0x55, 'V': 0x56, 'W': 0x57, 
            'X': 0x58, 'Y': 0x59, 'Z': 0x5A, '\[': 0x5B, '\\': 0x5C, '\]': 0x5D, '^': 0x5E, '_': 0x5F,
	}

	# Text viewport
        self._text_buffer = ""
        self._viewport = []
        self._viewport_pos = 0
    
    def connect(self):
        # Connect to MCP device
        self._mcp = MCP23017(self._i2c, address=self._addr)
        
        # Set all GPIO as output and set it to 0
        if self._mcp != None:
            self._mcp.iodir = 0x00
            self._mcp.gpio = 0

        return self._mcp == None

    def blank_viewport(self):
        for v_i in range (len(self._viewport)):
           self._print_character(' ', self._viewport[v_i][0], self._viewport[v_i][1])

    def _print_character(self, ascii_char, module, position):
        self._mcp.gpiob = 0xFC | ((position << 6) >> 6)
        self._mcp.gpiob &= ~(0x01 << (module + 2))
        self._mcp.gpioa = 0x80 | (self._character[ascii_char] if ascii_char in self._character.keys() else 0x20)
        self._mcp.gpiob = 0xFC

    def print_text(self):
        for v_i in range (len(self._viewport)):
            t_i = (self._viewport_pos + v_i) % len(self._text_buffer)
            self._print_character(self._text_buffer[t_i], self._viewport[v_i][0], self._viewport[v_i][1])  	
    @property
    def text(self):
        return self._text_buffer

    @text.setter
    def text(self, val):
        self._text_buffer = val
        self._viewport_pos = 0

    @property
    def viewport(self):
        return self._viewport

    @viewport.setter
    def viewport(self, val):
        self._viewport = val
        self._viewport_pos = 0
        
    @property
    def viewport_pos(self):
        return self._viewport_pos

    @viewport_pos.setter
    def viewport_pos(self, val):
        self._viewport_pos = val 
  
