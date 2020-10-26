#!flask/bin/python
"""
    Main retroclock module. Flask server.
 
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

import sys
import time
import pyowm
import busio
import board
import signal
import socket 
import threading

from datetime import datetime, timedelta
from config import config, Nixie_mode, HP_mode
from flask import Flask, request, abort, jsonify

import RPi.GPIO as GPIO
from datetime import datetime
from MCP23017.MCP23017_Nixie import MCP23017_Nixie_DigitController
from MCP23017.MCP23017_HPDL_1414 import MCP23017_HPDL_1414_CharacterController

class ClockWorker (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

		# Init relay GPIO setup, default disconnected
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(config["nixie_config"]["nixie_relay_gpio"],
			GPIO.OUT, initial=GPIO.LOW)

		# Nixie digit controller initialization
		i2c = busio.I2C(board.SCL, board.SDA)
		self._digit_controller_a = MCP23017_Nixie_DigitController(i2c,
			config["nixie_config"]["nixie_driver_a"]["digits"],
			addr=config["nixie_config"]["nixie_driver_a"]["i2c_addr"])
		self._digit_controller_b = MCP23017_Nixie_DigitController(i2c,
			config["nixie_config"]["nixie_driver_b"]["digits"],
			addr=config["nixie_config"]["nixie_driver_b"]["i2c_addr"])

		# Connect to MCP
		self._digit_controller_a.connect()
		self._digit_controller_b.connect()

		self._working_time = 0
		self._working = False

	def stop (self):
		GPIO.setup(config["nixie_config"]["nixie_relay_gpio"],
			GPIO.OUT, initial=GPIO.LOW)
		self._working = False

	def tick (self):
		self._working_time = 0

	def run(self):
		self._working = True

		while self._working:
			time.sleep(1)
			
			# Check working time
			if self._working_time > config["general_config"]["general_public"]["turn_on_time"]:
				GPIO.setup(config["nixie_config"]["nixie_relay_gpio"],
					GPIO.OUT, initial=GPIO.LOW)
			else:
				self._working_time += 1
				GPIO.setup(config["nixie_config"]["nixie_relay_gpio"],
					GPIO.OUT, initial=GPIO.HIGH)

			now = datetime.now()
			nixie_public = config["nixie_config"]["nixie_public"]
			if nixie_public["nixie_mode"] == Nixie_mode.H24:
				nixie_public["nixie_value_h"] = now.hour
				nixie_public["nixie_value_m"] = now.minute
				nixie_public["nixie_value_s"] = now.second

			elif nixie_public["nixie_mode"] == Nixie_mode.H12:
				nixie_public["nixie_value_h"] = now.hour % 12
				nixie_public["nixie_value_m"] = now.minute
				nixie_public["nixie_value_s"] = now.second

			elif nixie_public["nixie_mode"] == Nixie_mode.COUNTDOWN:
				# Substract 1 second
				nixie_public["nixie_value_s"] -= 1

				# Cascade through minutes and hours
				if nixie_public["nixie_value_s"] < 0:
					nixie_public["nixie_value_s"] = 59
					nixie_public["nixie_value_m"] -= 1

				if nixie_public["nixie_value_m"] < 0:
					nixie_public["nixie_value_m"] = 59
					nixie_public["nixie_value_h"] -= 1

				if nixie_public["nixie_value_h"] < 0:
					nixie_public["nixie_value_h"] = 0

			elif nixie_public["nixie_mode"] == Nixie_mode.STOPWATCH:
				
				# Add 1 second
				nixie_public["nixie_value_s"] += 1

				# Cascade through minutes and hours
				if nixie_public["nixie_value_s"] == 60:
					nixie_public["nixie_value_s"] = 0
					nixie_public["nixie_value_m"] += 1

				if nixie_public["nixie_value_m"] == 60:
					nixie_public["nixie_value_m"] = 0
					nixie_public["nixie_value_h"] += 1

				if nixie_public["nixie_value_h"] == 100:
					nixie_public["nixie_value_h"] = 0
					nixie_public["nixie_value_m"] = 0
					nixie_public["nixie_value_s"] = 0
			
			else: # CUSTOM
				pass

			# Print on nixies
			dots_value = nixie_public["nixie_value_s"] % 2
			self._digit_controller_a.dot1 = dots_value
			self._digit_controller_a.dot2 = dots_value
			self._digit_controller_b.dot1 = dots_value
			self._digit_controller_b.dot2 = dots_value
			self._digit_controller_a.ms_digit = int(nixie_public["nixie_value_h"] / 10)
			self._digit_controller_a.m_digit = int(nixie_public["nixie_value_h"] % 10)
			self._digit_controller_a.ls_digit = int(nixie_public["nixie_value_m"] / 10)
			self._digit_controller_b.ms_digit = int(nixie_public["nixie_value_m"] % 10)
			self._digit_controller_b.m_digit = int(nixie_public["nixie_value_s"] / 10)
			self._digit_controller_b.ls_digit = int(nixie_public["nixie_value_s"] % 10)

class HPWorker (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)

		# Config HP manager
		i2c = busio.I2C(board.SCL, board.SDA)
		self._co = MCP23017_HPDL_1414_CharacterController(i2c,
					config["hp_config"]["i2c_addr"])
		self._co.viewport = config["hp_config"]["viewport"]
		self._co.connect()

		# Init OWM service
		self._owm = pyowm.OWM(config["hp_config"]["owm_api_key"]) 
		self._weather_info = ""

		self._display = True
		self._working = False

	def stop (self):
		self._working = False

	def tick (self):
		self._display = True

	def run(self):
		self._working = True

		while self._working:
			time.sleep(1)			

			if self._display:
				hp_public = config["hp_config"]["hp_public"]
				
				# Gather time information
				now = datetime.now()
				time_info = now.strftime(hp_public["hp_date_format"]).upper()

				# Gather network info
				network_info = ""
				try: 
					host_name = socket.gethostname() 
					host_ip = socket.gethostbyname(host_name) 
					network_info = "{0} {1}".format(host_ip, host_name)
				except: 
					network_info = "No Network connected"

				# Gather weather info
				if self._weather_info is "" or now.minute == 0:
					observation = self._owm.weather_at_place(config["hp_config"]["owm_place"])
					w = observation.get_weather()
					self._weather_info = "{3} Temp: {0}^C Hum:{1}% Press:{2}mmHg ".format(
						w.get_temperature(unit='celsius')["temp"],
						w.get_humidity(),
						w.get_pressure()["press"],
						w.get_detailed_status()
					).upper()

				# Build text based on mode
				if hp_public["hp_mode"] == HP_mode.ROLLING:
					self._co.text = "{0} {1} {2}".format(
						time_info, network_info, self._weather_info
					)
				elif hp_public["hp_mode"] == HP_mode.DATE:
					self._co.text = time_info
				elif hp_public["hp_mode"] == HP_mode.WEATHER:
					self._co.text = self._weather_info
				elif hp_public["hp_mode"] == HP_mode.NETWORK:
					self._co.text = network_info
				else: # CUSTOM
					pass

				self._co.print_text()
				
				# Show screen for working time
				while datetime.now() < now + timedelta(seconds=config["general_config"]["general_public"]["turn_on_time"]): 
					self._co.print_text()
					self._co.viewport_pos += 1
					time.sleep(config["hp_config"]["viewport_speed"])

				# Blank after working time
				self._co.blank_viewport()
				self._display = False

app = Flask(__name__)
clock_worker = ClockWorker()
hp_worker = HPWorker()

@app.route('/api/v1/general', methods=['GET'])
def get_general():
	return jsonify(config['general_config']["general_public"])

@app.route('/api/v1/general', methods=['POST'])
def set_general():
	if not request.json:
		abort(400)
	for key in config['general_config']["general_public"]:
		if key in request.json:
			config['general_config']["general_public"][key] = request.json[key]
	return get_general(), 201

@app.route('/api/v1/nixie', methods=['GET'])
def get_nixie():
	return jsonify(config['nixie_config']["nixie_public"])

@app.route('/api/v1/nixie', methods=['POST'])
def set_nixie():
	if not request.json:
		abort(400)
	for key in config['nixie_config']["nixie_public"]:
		if key in request.json:
			config['nixie_config']["nixie_public"][key] = request.json[key]
	return get_general(), 201

@app.route('/api/v1/tick', methods=['GET'])
def tick():
	hp_worker.tick()
	clock_worker.tick()
	return jsonify(config['nixie_config']["nixie_public"])

@app.route('/api/v1/hp', methods=['GET'])
def get_hp():
	return jsonify(config['hp_config']["hp_public"])

@app.route('/api/v1/hp', methods=['POST'])
def set_hp():
	if not request.json:
		abort(400)
	for key in config['hp_config']["hp_public"]:
		if key in request.json:
			config['hp_config']["hp_public"][key] = request.json[key]
	return get_general(), 201


if __name__ == '__main__':

	# Run workers
	clock_worker.start()
	hp_worker.start()

	# Signal handler
	def signal_handler(sig, frame):
		clock_worker.stop()
		hp_worker.stop()
		sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)

	# Run Flask worker
	app.run("0.0.0.0", debug=False)
