# Octoprint-Smart-Filament-Sensor

[OctoPrint](http://octoprint.org/) plugin that lets integrate Smart Filament Sensors like BigTreeTechs SmartFilamentSensor directly to RaspberryPi GPIO pins. This enables that this sensor can also be used on 3D Printers, that do not have a E0-Stop like e.g. Creality 1.1.4 Mainboard of Ender 3.

Initial work based on the [Octoprint-Filament-Reloaded](https://github.com/kontakt/Octoprint-Filament-Reloaded) plugin by kontakt.
Fork of [Octoprint-Filament-Revolutions]https://github.com/RomRider/Octoprint-Filament-Revolutions plugin by RomRider.

The solution for this plugin is inspired by [Marlin Firmware](https://github.com/MarlinFirmware/Marlin)

## Required sensor

To use this plugin a Filament Sensor is needed that sends a toogling digital signal (0-1-0...) during movement.

This plugin can use the GPIO.BOARD or GPIO.BCM numbering scheme.

## Features

* Configurable GPIO pins.
* Support movement detection sensors, e.g. Smart-Filament-Sensor.
* Detect if filament is not moving anymore (jammed or runout)

## Installation

* Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager).
* Manually using this URL: https://github.com/maocypher/Octoprint-Smart-Filament-Sensor/archive/master.zip

After installation a restart of Octoprint is recommended.

## Configuration
### Detection time
Currently it is necessary to configure a maximum time period no filament movement was detected. This time could be depended on the print speed and maximum print line length. For the beginning - until I figured out how to estimate the best detection time - you can run a test print and messearue your maximum time and configure this value.
The default value 45 seconds was estimated on max. print speed 10mm/s, for faster prints it could be smaller.

### Octoprint - Firmware & Protocol
Since currently GCode command M600 is used to interrupt the print, it is recommended to add M600 to the setting "Pausing commands".

### Octoprint - GCode Scripts
If you do not want that the print is paused right on your print, I recommend to add a GCode Script for "After print job is paused". Also adding GCode script "Before print job is resumed" might be useful, in the case you hit the heatbed or print head during the change of the filament or removing the blockage.

## Disclaimer
I as author of this plugin am not responsible for any damages on your print or printer. As user you are responsible for a sensible usage of this plugin.

## Outlook
Detection based on distance