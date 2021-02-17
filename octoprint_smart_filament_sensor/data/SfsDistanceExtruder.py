#### Python ####
import json

#### Raspberry ####
import RPi.GPIO as GPIO

#### Plugin ####
from octoprint_smart_filament_sensor.data.ISfsExtruder import ISfsExtruder

# For multi extruder every extruder could have the same data
# - A filament sensor
# - Distance measurements
# - Timout measurements
class SfsDistanceExtruder(ISfsExtruder):

#### Distance Detection ####
    # The remaining distance of the extruder
    @property
    def remaining_distance(self):
        return self._remaining_distance

    @remaining_distance.setter
    def remaining_distance(self, value):
        self._remaining_distance = value
        self.cbRefreshUI(self)

    # The last extruder position
    @property
    def lastE(self):
        return self._lastE

    @lastE.setter
    def lastE(self, value):
        self._lastE = value

    # The current extruder position
    @property
    def currentE(self):
        return self._currentE

    @currentE.setter
    def currentE(self, value):
        self._currentE = value

    # Constructor
    # pPin = the GPIO pin for data
    # pSensorEnabled = enables or disables the sensor
    # pRemainingDistance = the start value for the remaining distance in distance detection mode
    def __init__(self, pLogger, pPin, pSensorEnabled, pCbStoppedMoving=None, pCbRefreshUI=None):
        super().__init__(pLogger, pPin, pSensorEnabled, pCbStoppedMoving, pCbRefreshUI)

        self.DETECTION_DISTANCE = -1
        self.START_DISTANCE_OFFSET = 7
        self._remaining_distance = -1
        self._filament_moving = False
        self._lastE = -1
        self._currentE = -1

        #self.init_gpio_pin()

    def setup(self, pRemainingDistance, pAbsolutExtrusion):
        self.DETECTION_DISTANCE = pRemainingDistance
        self.absolut_extrusion = pAbsolutExtrusion
        self.remaining_distance = self.DETECTION_DISTANCE + self.START_DISTANCE_OFFSET

    def filament_moved(self, pCurrentE=None):
        if(self.is_enabled == True):
            if(pCurrentE is not None):
                if (self.absolut_extrusion):
                    # LastE is not used and set to the same value as currentE
                    if (self._lastE == -1):
                        self._lastE = pCurrentE
                    else:
                        self._lastE = self._currentE
                    self._currentE = pCurrentE

                    self._logger.debug("LastE: " + str(self._lastE) + "; CurrentE: " + str(self._currentE))

                self._logger.debug("Remaining Distance: " + str(self.remaining_distance))

                if(self.remaining_distance > 0):
                    # Calculate the remaining distance from detection distance
                    # currentE - lastE is the delta distance
                    if(self.absolut_extrusion):
                        deltaDistance = self._currentE - self._lastE
                    # With relative extrusion the current extrusion value is the delta distance
                    else:
                        deltaDistance = float(pCurrentE)
                    if(deltaDistance > self.DETECTION_DISTANCE):
                        # Calculate the deltaDistance modulo the motion_sensor_detection_distance
                        # Sometimes the polling of M114 is inaccurate so that with the next poll
                        # very high distances are put back followed by zero distance changes
                        deltaDistance = deltaDistance % self.DETECTION_DISTANCE

                    self._logger.debug("Delta Distance: " + str(deltaDistance))
                    self.remaining_distance = (self.remaining_distance - deltaDistance)

                else:
                    self.cbFilamentStopped()
        else:
            self._logger.debug("Sensor for tool %r is disabled" % (self.pin))

    #def reset_distance (self):
    def gpio_event (self, pPin):
        self._logger.debug("Motion sensor detected movement")
        if(self.remaining_distance < self.DETECTION_DISTANCE):
            self.remaining_distance = self.DETECTION_DISTANCE
            self.filament_moving = True

    # Initialize the distance detection values
    def init_distance_detection(self):
        self._lastE = float(-1)
        self._currentE = float(0)
        self.reset_remaining_distance()

    # Reset the remaining distance on start or resume
    # START_DISTANCE_OFFSET is used for the (re-)start sequence
    def reset_remaining_distance(self):
        self.remaining_distance = (float(self.DETECTION_DISTANCE) + self.START_DISTANCE_OFFSET)

    def toJSON(self):
        jsonObject = {
            "filament_moving": self.filament_moving,
            "absolut_extrusion": self.absolut_extrusion,
            "is_enabled": self.is_enabled,
            "remaining_distance": self.remaining_distance
        }
        #return jsonObject
        return json.dumps(jsonObject, default=lambda o: o.__dict__, sort_keys=True, indent=4)