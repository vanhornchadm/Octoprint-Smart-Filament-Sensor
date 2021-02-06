# For multi extruder every extruder could have the same data
# - A filament sensor
# - Distance measurements
# - Timout measurements
class SmartFilamentSensorExtruderData(object):
    # The GPIO pin of the sensor
    @property
    def motion_sensor_pin(self):
        return self._motion_sensor_pin

    @motion_sensor_pin.setter
    def motion_sensor_pin(self, value):
        self._motion_sensor_pin = value
        self.callbackUpdateUI()

    # Enables or disables the sensor
    @property
    def motion_sensor_enabled(self):
        return self._motion_sensor_enabled

    @motion_sensor_enabled.setter
    def motion_sensor_enabled(self, value):
        self._motion_sensor_enabled = value
        self.callbackUpdateUI()

    # The last status of the filament
    @property
    def filament_moving(self):
        return self._filament_moving

    @filament_moving.setter
    def filament_moving(self, value):
        self._filament_moving = value
        self.callbackUpdateUI()

# Distance Detection
    # The remaining distance of the extruder
    @property
    def remaining_distance(self):
        return self._remaining_distance

    @remaining_distance.setter
    def remaining_distance(self, value):
        self._remaining_distance = value
        self.callbackUpdateUI()

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

# Timeout detection
    # The last point in time the extruder moved
    @property
    def last_motion_detected(self):
        return self._last_motion_detected

    @last_motion_detected.setter
    def last_motion_detected(self, value):
        self._last_motion_detected = value
        self.callbackUpdateUI()

    # Constructor
    # pPin = the GPIO pin for data
    # pSensorEnabled = enables or disables the sensor
    # pRemainingDistance = the start value for the remaining distance in distance detection mode
    def __init__(self, pPin, pSensorEnabled, pRemainingDistance):
        self._motion_sensor_pin = pPin
        self._motion_sensor_enabled = pSensorEnabled
        self._remaining_distance = pRemainingDistance
        
        self._filament_moving = False
        self._lastE = -1
        self._currentE = -1
        self._last_motion_detected = ""