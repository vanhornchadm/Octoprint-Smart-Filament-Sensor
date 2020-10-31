# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
from octoprint.events import Events
import RPi.GPIO as GPIO
from time import sleep
from flask import jsonify
import json
from octoprint_smart_filament_sensor.filament_motion_sensor_distance_detection import FilamentMotionSensorDistanceDetection
from octoprint_smart_filament_sensor.filament_motion_sensor_timeout_detection import FilamentMotionSensorTimeoutDetection

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
        self.motion_sensor = None

#Properties
    #@property
    #def motion_sensor_number(self):
    #    return int(self._settings.get(["motion_sensor_number"]))

    @property
    def motion_sensor_pin_0(self):
        return int(self._settings.get(["motion_sensor_pin_0"]))

    @property
    def motion_sensor_pin_1(self):
        return int(self._settings.get(["motion_sensor_pin_1"]))

    @property
    def motion_sensor_pin_2(self):
        return int(self._settings.get(["motion_sensor_pin_2"]))

    @property
    def motion_sensor_pin_3(self):
        return int(self._settings.get(["motion_sensor_pin_3"]))

    @property
    def motion_sensor_enabled_0(self):
        return self._settings.get_boolean(["motion_sensor_enabled_0"])

    @property
    def motion_sensor_enabled_1(self):
        return self._settings.get_boolean(["motion_sensor_enabled_1"])

    @property
    def motion_sensor_enabled_2(self):
        return self._settings.get_boolean(["motion_sensor_enabled_2"])

    @property
    def motion_sensor_enabled_3(self):
        return self._settings.get_boolean(["motion_sensor_enabled_3"])

    @property
    def motion_sensor_pause_print(self):
        return self._settings.get_boolean(["motion_sensor_pause_print"])

    @property
    def detection_method(self):
        return int(self._settings.get(["detection_method"]))

#Distance detection
    @property
    def motion_sensor_detection_distance(self):
        return int(self._settings.get(["motion_sensor_detection_distance"]))

    @property
    def motion_sensor_sampling_time(self):
        return int(self._settings.get(["motion_sensor_sampling_time"]))

#Timeout detection
    @property
    def motion_sensor_max_not_moving(self):
        return int(self._settings.get(["motion_sensor_max_not_moving"]))

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

        if self.motion_sensor_is_enabled() == False:
            self._logger.warn("Motion sensors are deactivated")
        self.motion_sensor_filament_moving = True
        self.motion_sensor = None

    def on_after_startup(self):
        self._logger.info("Smart Filament Sensor started")
        self._setup_sensor()

    def get_settings_defaults(self):
        return dict(
            #Motion sensor
            mode=0,    # Board Mode
            motion_sensor_enabled_0 = True, #Sensor detection is enabled by default
            motion_sensor_enabled_1 = False, #Sensor detection is enabled by default
            motion_sensor_enabled_2 = False, #Sensor detection is enabled by default
            motion_sensor_enabled_3 = False, #Sensor detection is enabled by default
            motion_sensor_number=1,  # By default only one sensor is used
            motion_sensor_pin_0=-1,  # Default is no pin
            motion_sensor_pin_1=-1,  # Default is no pin
            motion_sensor_pin_2=-1,  # Default is no pin
            motion_sensor_pin_3=-1,  # Default is no pin
            detection_method = 0, # 0 = timeout detection, 1 = distance detection

            # Distance detection
            motion_sensor_detection_distance = 3, # Recommended detection distance from Marlin would be 7
            motion_sensor_sampling_time = 10000, # It is recommended to choose sampling time not too low, because it would block the printer

            # Timeout detection
            motion_sensor_max_not_moving=45,  # Maximum time no movement is detected - default continously
            #send_gcode_only_once=False,  # Default set to False for backward compatibility
        )

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self._setup_sensor()

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=False)]

# Sensor methods
    def motion_sensor_start(self):
        if self.motion_sensor_is_enabled() and self.motion_sensor == None:

            # Distance detection
            if (self.detection_method == 1):
                if(self.motion_sensor_enabled_0 and self.motion_sensor_pin_0 > 0):
                    GPIO.setup(self.motion_sensor_pin_0, GPIO.IN)

                if(self.motion_sensor_enabled_1 and self.motion_sensor_pin_1 > 0):
                    GPIO.setup(self.motion_sensor_pin_1, GPIO.IN)

                if(self.motion_sensor_enabled_2 and self.motion_sensor_pin_2 > 0):
                    GPIO.setup(self.motion_sensor_pin_2, GPIO.IN)

                if(self.motion_sensor_enabled_3 and self.motion_sensor_pin_3 > 0):
                    GPIO.setup(self.motion_sensor_pin_3, GPIO.IN)

                # Add reset_distance if detection_method is distance_detection
                if(self.motion_sensor_enabled_0 and self.motion_sensor_pin_0 > 0):
                    GPIO.add_event_detect(self.motion_sensor_pin_0, GPIO.BOTH, callback=self.reset_distance)

                if(self.motion_sensor_enabled_1 and self.motion_sensor_pin_1 > 0):
                    GPIO.add_event_detect(self.motion_sensor_pin_1, GPIO.BOTH, callback=self.reset_distance)

                if(self.motion_sensor_enabled_2 and self.motion_sensor_pin_2 > 0):
                    GPIO.add_event_detect(self.motion_sensor_pin_2, GPIO.BOTH, callback=self.reset_distance)

                if(self.motion_sensor_enabled_3 and self.motion_sensor_pin_3 > 0):
                    GPIO.add_event_detect(self.motion_sensor_pin_3, GPIO.BOTH, callback=self.reset_distance)


                samplingTime = self.motion_sensor_sampling_time/1000
                self.motion_sensor = FilamentMotionSensorDistanceDetection(1, "MotionSensorDistanceDetectionThread", self._printer, samplingTime)
                self.remaining_distance = self.motion_sensor_detection_distance
                self.motion_sensor.start()
                self._logger.info("Motion sensor started: Distance detection")

            # Timeout detection
            elif (self.detection_method == 0):
                self.motion_sensor = FilamentMotionSensorTimeoutDetection(1, "MotionSensorTimeoutDetectionThread", self.motion_sensor_max_not_moving, self._logger, 
                    self.motion_sensor_pin_0, self.motion_sensor_pin_1, self.motion_sensor_pin_2, self.motion_sensor_pin_3, pCallback=self.printer_change_filament)
                self.motion_sensor.start()
                self._logger.info("Motion sensor started: Timeout detection")

            self.send_code = False

    def motion_sensor_stop(self):
        if(self.motion_sensor != None):
            self.motion_sensor.keepRunning = False
            self.motion_sensor = None
            self._logger.info("Motion sensor stopped")

            if (self.detection_method == 1):
                if(self.motion_sensor_enabled_0 and self.motion_sensor_pin_0 > 0):
                    GPIO.remove_event_detect(self.motion_sensor_pin_0)

                if(self.motion_sensor_enabled_1 and self.motion_sensor_pin_1 > 0):
                    GPIO.remove_event_detect(self.motion_sensor_pin_1)

                if(self.motion_sensor_enabled_2 and self.motion_sensor_pin_2 > 0):
                    GPIO.remove_event_detect(self.motion_sensor_pin_2)

                if(self.motion_sensor_enabled_3 and self.motion_sensor_pin_3 > 0):
                    GPIO.remove_event_detect(self.motion_sensor_pin_3)

    def motion_sensor_is_enabled(self):
        if(self.motion_sensor_enabled_0 or
            self.motion_sensor_enabled_1 or
            self.motion_sensor_enabled_2 or
            self.motion_sensor_enabled_3):
            return True
        else:
            return False

# Sensor callbacks
    def printer_change_filament (self):
        if(not self.send_code):
            #self._logger.debug("Motion sensor detected no movement")
            #self._printer.pause_print()        
            self._printer.commands("M600")
            self.send_code = True

    def reset_distance (self, pPin):
        #self._logger.debug("Motion sensor detected movement")
        if(self.remaining_distance < self.motion_sensor_detection_distance):
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
            if self.motion_sensor_is_enabled():
                self.motion_sensor_stop()

        # Disable motion sensor if paused
        elif event is Events.PRINT_PAUSED:
            self.print_started = False
            if self.motion_sensor_is_enabled():
                self.motion_sensor_stop()

        elif event is Events.POSITION_UPDATE:
            #TODO Distance Detection
            if(self.detection_method == 1):
                if (self.lastE == -1):
                    self.lastE = payload.get('e')
                else:
                    self.lastE = self.currentE
                self.currentE = payload.get('e')

                #self._logger.debug("Remaining Distance: " + str(self.remaining_distance))
                #self._logger.info("LastE: " + str(self.lastE) + "; CurrentE: " + str(self.currentE))
                if(self.remaining_distance > 0):
                    # Calculate the remaining distance from detection distance
                    # currentE - lastE is the delta distance
                    deltaDistance = self.currentE - self.lastE
                    if(deltaDistance > self.motion_sensor_detection_distance):
                        # Calculate the deltaDistance modulo the motion_sensor_detection_distance
                        # Sometimes the polling of M114 is inaccurate so that with the next poll
                        # very high distances are put back followed by zero distance changes
                        deltaDistance = deltaDistance % self.motion_sensor_detection_distance
                    #self._logger.debug("Delta Distance: " + str(deltaDistance))
                    self.remaining_distance = self.remaining_distance - deltaDistance
                else:
                    self.printer_change_filament()

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
                pip="https://github.com/maocypher/Octoprint-Smart-Filament-Sensor/archive/master.zip"
            )
        )


__plugin_name__ = "Smart Filament Sensor"
__plugin_version__ = "1.2.0"
__plugin_pythoncompat__ = ">=2.7,<4"

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
