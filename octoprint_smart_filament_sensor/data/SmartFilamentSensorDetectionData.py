import json
from octoprint_smart_filament_sensor.data.SmartFilamentSensorExtruderData import SmartFilamentSensorExtruderData
from octoprint_smart_filament_sensor.data.ConnectionTest import ConnectionTest

# Data for the detection
class SmartFilamentSensorDetectionData(object):
    # Is the print started
    @property
    def print_started(self):
        return self._print_started

    @print_started.setter
    def print_started(self, value):
        self._print_started = value

    # Extrusion mode (true = absolut extrusion; false = relative extrusion)
    @property
    def filament_moving(self):
        return self._filament_moving

    @filament_moving.setter
    def filament_moving(self, value):
        self._filament_moving = value
        self.callbackUpdateUI()

    # The last point in time the extruder moved
    @property
    def last_motion_detected(self):
        return self._last_motion_detected

    @last_motion_detected.setter
    def last_motion_detected(self, value):
        self._last_motion_detected = value
        self.callbackUpdateUI()

    @property
    def absolut_extrusion(self):
        return self._absolut_extrusion

    @absolut_extrusion.setter
    def absolut_extrusion(self, value):
        self._absolut_extrusion = value

#### Extruder ####
    # The current selected tool (extruder)
    @property
    def tool(self):
        return self._tool

    @tool.setter
    def tool(self, value):
        self._tool = value

    # All extruders connected with sensors
    @property
    def extruders(self):
        return self._extruders

    @extruders.setter
    def extruders(self, value):
        self._extruders = value

#### Connection-Test ####
    # Is the connection test running
    @property
    def connection_test_running(self):
        return self._connection_test_running

    @connection_test_running.setter
    def connection_test_running(self, value):
        self._connection_test_running = value
        self.callbackUpdateUI()

    @property
    def gpio_pin_connection_test(self):
        return self._gpio_pin_connection_test

    @gpio_pin_connection_test.setter
    def gpio_pin_connection_test(self, value):
        self._gpio_pin_connection_test = value
        self.callbackUpdateUI()

    @property
    def connectionTest(self):
        return self._connectionTest

    @connectionTest.setter
    def connectionTest(self, value):
        self._connectionTest = value

    # Constructor
    def __init__(self, pLogger, pRemainingDistance, pAbsolutExtrusion, pCallback=None):
        self._logger = pLogger
        self._remaining_distance = pRemainingDistance
        self._absolut_extrusion = pAbsolutExtrusion
        # The START_DISTANCE_OFFSETS solves the problem of false detections after the print start
        self.START_DISTANCE_OFFSET = 7
        self.callbackUpdateUI = pCallback

        # Default values
        self._connection_test_running = False
        self._print_started = False
        self._lastE = -1
        self._currentE = -1
        self._last_motion_detected = ""
        self._filament_moving = False
        self._tool = 0
        self._extruders = []
        self._gpio_pin_connection_test = -1
        self.connectionTest = ConnectionTest(self._logger, self.connectionTestCallback)

#### Extruders ####
    # Adds another extruder to the list of extruders and saves it into settings
    def addExtruder(self, pPin):
        self._extruders.append(SmartFilamentSensorExtruderData(pPin, False))
        converted = []

        for extr in self._extruders:
            converted.append(extr.ToYAML())

        return converted

    # Loads all extruders from settings into objects
    def loadExtruders(self, pExtr):
        self._logger.debug("Start method: loadExtruders")
        loaded = []
        for extr in pExtr:
            loaded.append(SmartFilamentSensorExtruderData(extr["pin"], extr["isEnabled"]))

        self._extruders = loaded

        self._logger.debug("End method: loadExtruders")

#### Connection Test ####
    def firstEnabledExtruder(self):
        for extr in self.extruders:
            if (extr.is_enabled == True):
                return extr

    def startConnectionTest(self):
        self.gpio_pin_connection_test = self.firstEnabledExtruder().pin
        self.connection_test_running = self.connectionTest.start_connection_test(self.gpio_pin_connection_test)

    def stopConnectionTest(self):
        self.connection_test_running = not (self.connectionTest.stop_connection_test())

    def connectionTestCallback(self, pMoving, pLastMotionDetected):
        self._logger.debug("Movement detected: %r" % (pMoving))
        self.filament_moving = pMoving
        self._last_motion_detected = pLastMotionDetected

#### Format converters ####
    # Convert the current object into JSON
    def toJSON(self):
        jsonObject = {
            "print_started": self.print_started,
            "filament_moving": self.filament_moving,
            "last_motion_detected": self.last_motion_detected,
            "absolut_extrusion": self.absolut_extrusion,
            "connection_test_running": self.connection_test_running,
            "tool": self.tool,
            "remaining_distance": self._remaining_distance,
            "gpio_pin_connection_test": self.gpio_pin_connection_test
        }
        #return jsonObject
        return json.dumps(jsonObject, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    #def toYAML(self):
    #    data = {
    #        'print_started': self.print_started,
    #        'filament_moving': self.filament_moving,
    #        'last_motion_detected': self.last_motion_detected,
    #        'absolut_extrusion': self.absolut_extrusion,
    #        'connection_test_running': self.connection_test_running,
    #        'tool': self.tool,
    #        'remaining_distance': self._remaining_distance
    #    }

    #   return data