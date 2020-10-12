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
    global test

    def initialize(self):
        self._logger.info(
            "Running RPi.GPIO version '{0}'".format(GPIO.VERSION))
        if GPIO.VERSION < "0.6":       # Need at least 0.6 for edge detection
            raise Exception("RPi.GPIO must be greater than 0.6")
        GPIO.setwarnings(False)        # Disable GPIO warnings

#Properties
    @property
    def motion_sensor_pin(self):
        return int(self._settings.get(["motion_sensor_pin"]))

    @property
    def motion_sensor_max_not_moving(self):
        return int(self._settings.get(["motion_sensor_max_not_moving"]))

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

    @property
    def send_gcode_only_once(self):
        return self._settings.get_boolean(["send_gcode_only_once"])

# Initialization methods
    def _setup_sensor(self):
        self.motion_sensor_filament_moving = True
        self.motion_sensor = None

        #TODO: motion sensor enabled logging
        if self.motion_sensor_enabled():
            if self.mode == 0:
                self._logger.info("Using Board Mode")
                GPIO.setmode(GPIO.BOARD)
            else:
                self._logger.info("Using BCM Mode")
                GPIO.setmode(GPIO.BCM)
        else:
            self._logger.info(
                "Pins not configured, won't work unless configured!")

    def on_after_startup(self):
        self._logger.info("Smart Filament Sensor started")
        self._setup_sensor()

    def get_settings_defaults(self):
        return dict(
            #Motion sensor
            motion_sensor_pin=-1,  # Default is no pin
            motion_sensor_max_not_moving=45,  # Maximum time no movement is detected - default continously
            #motion_sensor_gcode='',
            #motion_sensor_pause_print=True,

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
            self.motion_sensor = FilamentMotionSensor(1, "MotionSensorThread", self.motion_sensor_pin, self.motion_sensor_max_not_moving, pCallback=self.motion_sensor_callback)
            self.motion_sensor.start()
            self._logger.info("Motion sensor started")

    def motion_sensor_stop(self):
        if(self.motion_sensor != None):
            self.motion_sensor.keepRunning = False
            self.motion_sensor = None
            self._logger.info("Motion sensor stopped")

# Events
    def on_event(self, event, payload):     
        if event is Events.PRINT_RESUMED:
            self.motion_sensor_start()
        # Start motion sensor on first G1 command
        elif event is Events.Z_CHANGE:
            self.motion_sensor_start()         

        # Disable sensor
        elif event in (
            Events.PRINT_DONE,
            Events.PRINT_FAILED,
            Events.PRINT_CANCELLED,
            Events.ERROR
        ):
            self._logger.info("%s: Disabling filament sensors." % (event))
            if self.motion_sensor_enabled():
                self.motion_sensor_stop()

        # Disable motion sensor if paused
        elif event is Events.PRINT_PAUSED:
            if self.motion_sensor_enabled():
                self.motion_sensor_stop()

# Sensor callbacks
    def motion_sensor_callback (self):
        self._logger.info("Motion sensor detected no movement")
        self._printer.pause_print()        

# Plugin update methods
    #def get_update_information(self):
    #    return dict(
    #        smart_filament_sensor=dict(
    #            displayName="Smart Filament Sensor",
    #            displayVersion=self._plugin_version,

                # version check: github repository
                #type="github_release",
                #user="maocypher",
                #repo="Octoprint-Filament-Revolutions",
#                current=self._plugin_version,

                # update method: pip
                #pip="https://github.com/RomRider/Octoprint-Filament-Revolutions/archive/{target_version}.zip"
 #           )
  #      )


__plugin_name__ = "Smart Filament Sensor"
__plugin_version__ = "1.0.0"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = SmartFilamentSensor()

    #global __plugin_hooks__
    #__plugin_hooks__ = {
    #    "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    #}


def __plugin_check__():
    try:
        import RPi.GPIO
    except ImportError:
        return False

    return True
