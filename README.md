Retroclock 
----------
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


This is the code I made for one on my personal projects, a clock based on nixie tubes and LED bubble displays:
<p align="center">
    <img src="/images/assembly.gif">
</p>

I wanted to create a fancy clock with a retro look so I decided to investigate old display tecnologies. I like retro 
stuff and tinkering with electronic things so bought some stuff to test. I ended using old soviet ИН-12Б and
INS-1 tubes, and HP/Agilent HPDL-1414 LED bubble displays.

I also decided to hand solder all circuit boards because I really like the look of them:

<table float="center" style="text-align: center; width:100%; table-layout:fixed">
    <tr>
        <td><img width="450" src="/images/hand_solder_1.jpg"/></td>
        <td><img width="450" src="/images/hand_solder_2.jpg"/></td>
    </tr>
</table>

I share the code and the overall design just in case is useful to anyone. 

Nixie tubes
-----------
The module is based on 6 ИН-12Б tubes that shows the time and 4 INS-1 tubes that indicates the seconds. 

<table float="center" style="text-align: center; width:100%; table-layout:fixed">
    <tr>
        <td><img width="450" src="/images/nixie_module_1.gif"/></td>
        <td><img width="450" src="/images/nixie_module_2.jpg"/></td>
    </tr>
</table>

<img src="/images/nixie_module.png">

The high voltage needed for the nixies to work is produced by a high voltage 12-24v to 85-235v boost module
(NCH6100HV) configured to 180v. The boost module is fed with 12v through a NC relay controlled by a digital
signal from the pin 23 (BCM naming) that feeds a 2N2222 NPN transistor to be able to switch the state of the
relay with 12v. This way, for the 180v to reach the anodes of the nixies, a explicit 5v signal needs to be
generated (and maintained) by the software, so all nixies will be normally powered off to prevent wear and
ghosting of the tubes.

The nixie cathodes are managed using 5V digital signals using a high voltage BCD-to-decimal nixie controller
(К155ИД1). The BCD signals are controlled using a Raspberry Pi and a 16-Bit I/O Expander (MCP23017) controlled
via i2c. Two MCP23017 control 6 К155ИД1 ICs (3 each, 3x4 bits BCD) that manages all 6 ИН-12Б tubes. These 
MCP23017 ICs also controls 4 MPSA42 0.5A/300V NPN transistors that manages the cathode of the little 4 INS-1 tubes.
I am not using the decimal point present in ИН-12Б tubes.

For the ИН-12Б tubes, a 33KΩ current limitating resistor is placed on the anode and for the INS-1 the resistor
value is 270KΩ. With this values, aproximetely 1.2mA will flow through the ИН-12Б tubes and 0,5mA through the INS-1
at their respective (aproximated) sustaining voltages of 140v and 55v. I think that maybe a 1.2mA can cause
the ИН-12Б tubes to not be as bright as they should (maybe a 15K resistor will be better) but I think that the look
fine and this way the tubes will last longer.

A lot of the information about how nixies work, have been obtained from [this hackaday project](https://hackaday.io/project/1940-modular-nixie-display/log/11038-the-in-12a).

Datasheets and links:
 - ИН-12Б/IN-12B: [Datasheet](https://eandc.ru/news/detail.php?ID=23902)
 - INS-1: [Datasheet](http://www.tube-tester.com/sites/nixie/dat_arch/INS-1.pdf)
 - NCH6100HV: [Omnixie](https://omnixie.com/products/nch6100hv-nixie-hv-power-module)
 - К155ИД1: [Russian datasheet](https://eandc.ru/pdf/mikroskhema/k155id1.pdf), [Western equivalent IC](https://tubehobby.com/datasheets/k155id1.pdf)
 - 2N2222: [Datasheet](http://web.mit.edu/6.101/www/reference/2N2222A.pdf)
 - MCP23017: [Datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/20001952C.pdf)

LED bubble displays
-------------------
The module is based on 4 HPDL-1414 screens. This screen can show a total of 16 characters symultaneously, and can
be configured to show: date information, network information, weather information (retrieved from OpenWeatherMap using PyOWM) 
or any text. Text can also be configured to be static or to roll over the screen. The DIP switch changes i2c address for the 
MCP23017.

<table float="center" style="text-align: center; width:100%; table-layout:fixed">
    <tr>
        <td><img src="/images/hp_module_1.gif" width="450" ></td>
        <td><img width="450" src="/images/hp_module_2.jpg" width="450" ></td>
    </tr>
</table>

<p align="center">
    <img src="/images/led_display_module.png">
</p>

All 4 HPDL-1414 modules are connected to a MCP23017 I/O expander. All share the same 7 bits bus for data transmission
to the modules and the same 2 bit bus for digit selection. Digits are written on the displays by multiplexing the bus
using the WR pin on each module that is wired to independent bits of the I/O expander. Also one of the free bits left
on the I/O expander is used to power on all the modules using a 2N2222 NPN transistor. This way all modules can be 
switched off if needed. The MCP23017 I/O expander is also controlled by a raspberry Pi using I2c.

Datasheets and links:
 - HPDL-1414: [Datasheet](http://pdf.datasheetcatalog.com/datasheet/hp/HPDL-1414.pdf)
 - 2N2222: [Datasheet](http://web.mit.edu/6.101/www/reference/2N2222A.pdf)
 - PyOWM: [Docs](https://pyowm.readthedocs.io/en/latest/)
 - OpenWeatherMap: [Website](https://openweathermap.org/)

Raspberry Pi and REST service
-----------------------------
All the assembly is controlled by a Raspberry Pi using i2c. I went with the Raspberry Pi (original one) because of its
low power consumption and because I had one hanging arround. As a Linux capable device, I can have any other service also
deployed on the system.

The Raspberry is powered from an external 12v power supply (the same that powers the nixie high voltage booster) after
stepping down the 12v to 5v using a cheap Ebay step down converter.

The system is controlled by a simple Flask HTTP server that serves a REST service. The initial configuration of the service
is located in config.py and it is also a direct representation of the REST service. GET or POST requests to ```/api/v1/general```
```/api/v1/hp``` or ```/api/v1/nixie``` expose the configuration. 

The clock is by default idle (nothing is light up) and a request to ```/api/v1/tick``` will trigger both HP and nixie workers.
This will cause both nixies and HP screens will light up during 1 minute before returning to idle. All this behaviour can be modified
using the REST service or editing config.py.

All the service is written in python 3, so some dependencies need to be installed:
```
sudo apt-get install python3 python3-pip
```

In order to run the service, create a virtualenv and then install the dependencies:
```
cd <route of the project>
virtualenv -p /usr/bin/python3 venv
source venv/bin/activate
pip3 install -r requeriments.txt 

```
To run it, you can just run:
```
./run_retroclock.sh
```
If you want to start the service on startup, supervisor can be a good option:
```
sudo apt-get install supervisor
```
Create a new service file:
```
nano /etc/supervisor/conf.d/retroclock.conf
```
An example can be:
```
[program:retroclock]
command=/home/pi/nixieclock/run_retroclock.sh

stdout_logfile=/var/log/supervisor/%(program_name)s.log
stdout_logfile_maxbytes=200MB
stderr_logfile=/var/log/supervisor/%(program_name)s.log
stderr_logfile_maxbytes=200MB
startsecs=5
stopwaitsecs=5
autorestart=true
```
Reload everything:
```
supervisorctl reread
supervisorctl restart retroclock
```


About
-----

Copyright (c) 2020 Guillermo Climent, https://github.com/willyneutron

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
