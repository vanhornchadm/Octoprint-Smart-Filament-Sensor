# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
import RPi.GPIO as GPIO
from time import sleep
from flask import jsonify
import json
from octoprint_smart_filament_sensor.filament_motion_sensor import FilamentMotionSensor

class SmartFilamentSensor(octoprint.plugin.StartupPlugin,
                                 octoprint.plugin.EventHandlerPlugin,
                                 octoprint.plugin.TemplatePlugin,
                                 octoprint.plugin.SettingsPlugin):

    def initialize(self):
        self._logger.info(
            "Running RPi.GPIO version '{0}'".format(GPIO.VERSION))
        if GPIO.VERSION < "0.6":       # Need at least 0.6 for edge detection
            raise Exception("RPi.GPIO must be greater than 0.6")
        GPIO.setwarnings(False)        # Disable GPIO warnings

        self.print_started = False
        self.remaining_distance = self.motion_sensor_detection_distance
        self.lastE = -1
        self.currentE = -1
        self.send_code = False

#Properties
    @property
    def motion_sensor_pin(self):
        return int(self._settings.get(["motion_sensor_pin"]))

    @property
    def motion_sensor_detection_distance(self):
        return int(self._settings.get(["motion_sensor_detection_distance"]))

    #@property
    #def motion_sensor_sampling_time(self):
    #    return int(self._settings.get(["motion_sensor_sampling_time"]))

    @property
    def motion_sensor_pause_print(self):
        return self._settings.get_boolean(["motion_sensor_pause_print"])

    #@property
    #def motion_sensor_gcode(self):
    #    return str(self._settings.get(["motion_sensor_gcode"])).splitlines()

#General Properties
    @property
    def mode(self):
        return int(self._settings.get(["mode"]))

    #@property
    #def send_gcode_only_once(self):
    #    return self._settings.get_boolean(["send_gcode_only_once"])

# Initialization methods
    def _setup_sensor(self):
        if(self.mode == 0):
            self._logger.info("Using Board Mode")
            GPIO.setmode(GPIO.BOARD)
        else:
            self._logger.info("Using BCM Mode")
            GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.motion_sensor_pin, GPIO.IN)
        GPIO.add_event_detect(self.motion_sensor_pin, GPIO.BOTH, callback=self.reset_distance)

        if not self.motion_sensor_enabled():
            self._logger.info(
                "Pins not configured, won't work unless configured!")
        self.motion_sensor_filament_moving = True
        self.motion_sensor = None

    def on_after_startup(self):
        self._logger.info("Smart Filament Sensor started")
        self._setup_sensor()

    def get_settings_defaults(self):
        return dict(
            #Motion sensor
            motion_sensor_pin=-1,  # Default is no pin
            motion_sensor_detection_distance = 7, # Recommended detection distance from Marlin
            #motion_sensor_sampling_time = 250, # It is recommended to choose sampling time not too low, because it would block the printer

            mode=0,    # Board Mode
            #send_gcode_only_once=False,  # Default set to False for backward compatibility
        )

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self._setup_sensor()

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

# Sensor methods
    def motion_sensor_enabled(self):
        return self.motion_sensor_pin != -1

    def motion_sensor_start(self):
        if self.motion_sensor_enabled() and self.motion_sensor == None:
            #self.motion_sensor = FilamentMotionSensor(1, "MotionSensorThread", self._printer, (self.motion_sensor_sampling_time/1000))
            self.motion_sensor = FilamentMotionSensor(1, "MotionSensorThread", self._printer)
            self.motion_sensor.start()
            self.send_code = False
            self.remaining_distance = self.motion_sensor_detection_distance
            self._logger.info("Motion sensor started")

    def motion_sensor_stop(self):
        if(self.motion_sensor != None):
            self.motion_sensor.keepRunning = False
            self.motion_sensor = None
            self._logger.info("Motion sensor stopped")

# Sensor callbacks
    def printer_change_filament (self):
        self._logger.info("Motion sensor detected no movement")
        #self._printer.pause_print()        
        self._printer.commands("M600")
        self.send_code = True

    def reset_distance (self, pPin):
        self._logger.info("Motion sensor detected movement")
        self.remaining_distance = self.motion_sensor_detection_distance

# Events
    def on_event(self, event, payload):     
        if event is Events.PRINT_STARTED:
            self.print_started = True
        elif event is Events.PRINT_RESUMED:
            self.print_started = True
            self.motion_sensor_start()
        # Start motion sensor on first G1 command
        elif event is Events.Z_CHANGE:
            if(self.print_started):
                self.motion_sensor_start()         

        # Disable sensor
        elif event in (
            Events.PRINT_DONE,
            Events.PRINT_FAILED,
            Events.PRINT_CANCELLED,
            Events.ERROR
        ):
            self._logger.info("%s: Disabling filament sensors." % (event))
            self.print_started = False
            if self.motion_sensor_enabled():
                self.motion_sensor_stop()

        # Disable motion sensor if paused
        elif event is Events.PRINT_PAUSED:
            self.print_started = False
            if self.motion_sensor_enabled():
                self.motion_sensor_stop()

        elif event is Events.POSITION_UPDATE:
            if (self.lastE == -1):
                self.lastE = payload.get('e')
            else:
                self.lastE = self.currentE
            self.currentE = payload.get('e')

            if(self.remaining_distance > 0):
                # Calculate the remaining distance from detection distance
                # currentE - lastE is the delta distance
                self.remaining_distance = self.remaining_distance - (self.currentE - self.lastE)
                self._logger.info("Remaining Distance: " + str(self.remaining_distance))
            else:
                if(not self.send_code):
                    self.printer_change_filament()
            
            #time.sleep(0.250)

# Plugin update methods
    def get_update_information(self):
        return dict(
            smartfilamentsensor=dict(
                displayName="Smart Filament Sensor",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="maocypher",
                repo="Octoprint-Smart-Filament-Sensor",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/RomRider/Octoprint-Filament-Revolutions/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Smart Filament Sensor"
__plugin_version__ = "2.0.0"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = SmartFilamentSensor()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }


def __plugin_check__():
    try:
        import RPi.GPIO
    except ImportError:
        return False

    return True
