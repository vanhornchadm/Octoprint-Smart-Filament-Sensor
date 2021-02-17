#### Python ####
import threading
import time
import json

#### Raspberry ####
import RPi.GPIO as GPIO

#### Plugin ####
from octoprint_smart_filament_sensor.data.ISfsExtruder import ISfsExtruder
from octoprint_smart_filament_sensor.data.SfsTimeoutDetection import SfsTimeoutDetection

# For multi extruder every extruder could have the same data
# - A filament sensor
# - Distance measurements
# - Timout measurements
class SfsTimeoutExtruder(ISfsExtruder):

#### Timeout detection ####
    # The last point in time the extruder moved
    @property
    def last_motion_detected(self):
        return self._last_motion_detected

    @last_motion_detected.setter
    def last_motion_detected(self, value):
        self._last_motion_detected = value
        self.cbRefreshUI(self)

    # Constructor
    # pPin = the GPIO pin for data
    # pSensorEnabled = enables or disables the sensor
    # pRemainingDistance = the start value for the remaining distance in distance detection mode
    def __init__(self, pLogger, pPin, pSensorEnabled, pCbStoppedMoving=None, pCbRefreshUI=None):
        super().__init__(pLogger, pPin, pSensorEnabled, pCbStoppedMoving, pCbRefreshUI)

        self._last_motion_detected = ""

        self.init_gpio_pin()

    def setup(self, pMaxNotMovingTime, pAbsolutExtrusion):     
        self.max_not_moving_time = pMaxNotMovingTime
        self.absolut_extrusion = pAbsolutExtrusion

#### Sensor ####
    def start_sensor(self):
        self._thread = SfsTimeoutDetection(self.pin, "ConnectionTest", self.pin, self.max_not_moving_time, self._logger, self.cbFilamentMoving)
        self._thread.start()
        self.filament_moving = True
        self._logger.debug("Start Timeout detection")

    def stop_sensor(self):
        self._thread.keepRunning = False
        self._logger.debug("Stop Timeout detection")

    def cbFilamentMoving(self, pMoving, pLastMovement):
        self.filament_moving = pMoving
        self.last_motion_detected = pLastMovement

        if(self.filament_moving == False):
            self.cbFilamentStopped()

#### Converstion ###
    # Convert the current object into JSON
    def toJSON(self):
        jsonObject = {
            "filament_moving": self.filament_moving,
            "absolut_extrusion": self.absolut_extrusion,
            "is_enabled": self.is_enabled,
            "last_motion_detected": self.last_motion_detected,
            "gpio_pin_connection_test": self.pin
        }
        #return jsonObject
        return json.dumps(jsonObject, default=lambda o: o.__dict__, sort_keys=True, indent=4)