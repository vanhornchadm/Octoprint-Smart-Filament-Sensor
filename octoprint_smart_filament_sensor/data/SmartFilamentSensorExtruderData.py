import json

# For multi extruder every extruder could have the same data
# - A filament sensor
# - Distance measurements
# - Timout measurements
class SmartFilamentSensorExtruderData(object):
    # The GPIO pin of the sensor
    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        self._pin = value
        self.cbRefreshUI()

    # Enables or disables the sensor
    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        self._is_enabled = value
        self.cbRefreshUI()

    # The last status of the filament
    @property
    def filament_moving(self):
        return self._filament_moving

    @filament_moving.setter
    def filament_moving(self, value):
        self._filament_moving = value
        self.cbRefreshUI()

#### Distance Detection ####
    # The remaining distance of the extruder
    @property
    def remaining_distance(self):
        return self._remaining_distance

    @remaining_distance.setter
    def remaining_distance(self, value):
        self._remaining_distance = value
        self.cbRefreshUI()

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

#### Timeout detection ####
    # The last point in time the extruder moved
    @property
    def last_motion_detected(self):
        return self._last_motion_detected

    @last_motion_detected.setter
    def last_motion_detected(self, value):
        self._last_motion_detected = value
        self.cbRefreshUI()

#### Events ####
    @property
    def cbRefreshUI(self):
        return self._cbRefreshUI

    @cbRefreshUI.setter
    def cbRefreshUI(self, value):
        self._cbRefreshUI = value

#### Print ####
    @property
    def absolut_extrusion(self):
        return self._absolut_extrusion

    @absolut_extrusion.setter
    def absolut_extrusion(self, value):
        self._absolut_extrusion = value

    # Constructor
    # pPin = the GPIO pin for data
    # pSensorEnabled = enables or disables the sensor
    # pRemainingDistance = the start value for the remaining distance in distance detection mode
    def __init__(self, pLogger, pPin, pSensorEnabled):
        self._logger = pLogger
        self._pin = int(pPin)
        self._is_enabled = pSensorEnabled
        self.DETECTION_DISTANCE = -1
        self._absolut_extrusion = False
        self.cbFilamentStopped = None
        self._cbRefreshUI = None
        self.START_DISTANCE_OFFSET = -1
        self._remaining_distance = -1
        
        self._filament_moving = False
        self._lastE = -1
        self._currentE = -1
        self._last_motion_detected = ""

    def setup(self, pPin, pSensorEnabled, pRemainingDistance, pAbsolutExtrusion, pCbStoppedMoving=None, pCbUpdateUI=None):
        self._pin = pPin
        self._is_enabled = pSensorEnabled
        self.DETECTION_DISTANCE = pRemainingDistance
        self.absolut_extrusion = pAbsolutExtrusion
        self.cbFilamentStopped = pCbStoppedMoving
        self.cbRefreshUI = pCbUpdateUI
        self.START_DISTANCE_OFFSET = 7
        self.remaining_distance = self.DETECTION_DISTANCE + self.START_DISTANCE_OFFSET
        
        self._filament_moving = False
        self._lastE = -1
        self._currentE = -1
        self._last_motion_detected = ""

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

    def reset_distance (self):
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

    def ToYAML(self):
        data = {
            'pin': self._pin,
            'isEnabled': self._is_enabled
        }

        return data

    #def toJSON(self):
    #     return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)