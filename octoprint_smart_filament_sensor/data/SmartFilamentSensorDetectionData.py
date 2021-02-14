import json
import logging
from octoprint_smart_filament_sensor.filament_motion_sensor_timeout_detection import FilamentMotionSensorTimeoutDetection
from octoprint_smart_filament_sensor.data.SmartFilamentSensorExtruderData import SmartFilamentSensorExtruderData
from octoprint_smart_filament_sensor.data.ConnectionTest import ConnectionTest

# Data for the detection
class SmartFilamentSensorDetectionData(object):

#### Properties - Sensor ####
    # Extrusion mode (true = absolut extrusion; false = relative extrusion)
    @property
    def filament_moving(self):
        return self._filament_moving

    @filament_moving.setter
    def filament_moving(self, value):
        self._filament_moving = value
        self.cbRefreshUI()

    # The last point in time the extruder moved
    @property
    def last_motion_detected(self):
        return self._last_motion_detected

    @last_motion_detected.setter
    def last_motion_detected(self, value):
        self._last_motion_detected = value
        self.cbRefreshUI()

#### Properties - Print ####
    @property
    def absolut_extrusion(self):
        return self._absolut_extrusion

    @absolut_extrusion.setter
    def absolut_extrusion(self, value):
        self._absolut_extrusion = value
        self.setAbsolutExtrusionForAll(value)

    # Is the print started
    @property
    def print_started(self):
        return self._print_started

    @print_started.setter
    def print_started(self, value):
        self._print_started = value

    @property
    def send_pause_code(self):
        return self._send_pause_code

    @send_pause_code.setter
    def send_pause_code(self, value):
        self._send_pause_code = value

#### Properties - Extruder ####
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

#### Properties - Connection-Test ####
    # Is the connection test running
    @property
    def connection_test_running(self):
        return self._connection_test_running

    @connection_test_running.setter
    def connection_test_running(self, value):
        self._connection_test_running = value
        self.cbRefreshUI()

    @property
    def gpio_pin_connection_test(self):
        return self._gpio_pin_connection_test

    @gpio_pin_connection_test.setter
    def gpio_pin_connection_test(self, value):
        self._gpio_pin_connection_test = value
        self.cbRefreshUI()

    @property
    def connectionTest(self):
        return self._connectionTest

    @connectionTest.setter
    def connectionTest(self, value):
        self._connectionTest = value

#### Events ####
    @property
    def cbPausePrinter(self):
        return self._cbPausePrinter

    @cbPausePrinter.setter
    def cbPausePrinter(self, value):
        self._cbPausePrinter = value

    @property
    def cbRefreshUI(self):
        return self._cbRefreshUI

    @cbRefreshUI.setter
    def cbRefreshUI(self, value):
        self._cbRefreshUI = value

#### Constructor ####
    def __init__(self, pLogger, pRemainingDistance, pAbsolutExtrusion, pCbUpdateUI=None, pCbPausePrinter=None):
        self._logger = pLogger
        #self.init_logging()
        #self._remaining_distance = pRemainingDistance
        self._absolut_extrusion = pAbsolutExtrusion

        # Events
        self._cbRefreshUI = pCbUpdateUI
        self._cbPausePrinter = pCbPausePrinter

        # Const
        # The START_DISTANCE_OFFSETS solves the problem of false detections after the print start
        self.START_DISTANCE_OFFSET = 7
        self.DETECTION_DISTANCE = pRemainingDistance

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
        self._timoutDetection = None
        self._send_pause_code = False

        # Init
        self.connectionTest = ConnectionTest(self._logger, self.cbConnectionTest)
        self._logger.info("DetectionData initialized")

#### Logging ####
    def init_logging(self):
        # setup customized logger
        from octoprint.logging.handlers import CleaningTimedRotatingFileHandler

        self._logger = logging.getLogger('sfs.DetectionData')
        sfs_logging_handler = CleaningTimedRotatingFileHandler(
            'plugin_smartfilamentsensor.log',
            when="D",
            backupCount=3,
        )
        sfs_logging_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        )
        sfs_logging_handler.setLevel(logging.DEBUG)

        self._logger.addHandler(sfs_logging_handler)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

#### Extruders ####
    # Adds another extruder to the list of extruders and saves it into settings
    def addExtruder(self, pPin):
        self._extruders.append(SmartFilamentSensorExtruderData(self._logger, pPin, False))
        converted = []

        for extr in self._extruders:
            converted.append(extr.ToYAML())

        return converted

    # Loads all extruders from settings into objects
    def loadExtruders(self, pExtr):
        self._logger.debug("Start method: loadExtruders")
        loaded = []
        for extr in pExtr:
            loaded.append(SmartFilamentSensorExtruderData(self._logger, extr["pin"], extr["isEnabled"]))

        self._extruders = loaded

        self._logger.debug("End method: loadExtruders")

    def resetDistanceDetectionForAll(self):
        for extr in self.extruders:
            extr.reset_remaining_distance()

    def setAbsolutExtrusionForAll(self, pAbsolutExtrusion):
        for extr in self.extruders:
            extr.absolut_extrusion = pAbsolutExtrusion

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

    def cbConnectionTest(self, pMoving, pLastMotionDetected):
        self._logger.debug("Movement detected: %r" % (pMoving))
        self.filament_moving = pMoving
        self._last_motion_detected = pLastMotionDetected

#### Timeout detection ####
    def startTimeoutDetection(self, pMaxNotMoving):
        if (self._timoutDetection == None):
            self._logger.debug("Detection Mode: Timeout detection")
            self._logger.debug("Timeout: " + str(pMaxNotMoving))

            # Start Timeout_Detection thread
            self._timoutDetection = FilamentMotionSensorTimeoutDetection(1, "MotionSensorTimeoutDetectionThread", self.extruders[self.tool].pin, 
                pMaxNotMoving, self._logger, pCallback=self.cbPauseTimeoutDetection)
            self._timoutDetection.start()
            self._logger.info("Motion sensor started: Timeout detection")

            self.send_pause_code = False

    # Stop the motion_sensor thread
    def stopTimeoutDetection(self):
        if(self._timoutDetection != None):
            self._timoutDetection.keepRunning = False
            self._timoutDetection = None
            self._logger.info("Motion sensor stopped")

#### Distance detection ####
    def startDistanceDetection(self):
        for extr in self.extruders:
            extr.setup(extr.pin, extr.is_enabled, self.DETECTION_DISTANCE, self.absolut_extrusion, 
                pCbStoppedMoving=self.cbPauseDistanceDetection, pCbUpdateUI=self.cbRefreshUI)

#### Printer ####
    # Send configured pause command to the printer to interrupt the print
    def cbPauseTimeoutDetection (self, pMoving, pLastMotionDetected):
        self.filament_moving = pMoving
        self.last_motion_detected = pLastMotionDetected

        if(pMoving == False):
            # Check if stop signal was already sent
            if(not self.send_pause_code):
                self._logger.debug("Motion sensor detected no movement")
                #self._logger.info("Pause command: " + self.pause_command)   
                self.cbPausePrinter()
                self.send_pause_code = True

    def cbPauseDistanceDetection (self):
        self.filament_moving = False

        # Check if stop signal was already sent
        if(not self.send_pause_code):
            self._logger.debug("Motion sensor detected no movement")
            #self._logger.info("Pause command: " + self.pause_command)   
            self.cbPausePrinter()
            self.send_pause_code = True

    def cbRefreshUIExtruder(self):
        self.cbRefreshUI()

#### Format converters ####
    # Convert the current object into JSON
    def toJSON(self):
        jsonObject = {
            "print_started": self.print_started,
            "filament_moving": self.extruders[self.tool].filament_moving,
            "last_motion_detected": self.extruders[self.tool].last_motion_detected,
            "absolut_extrusion": self.absolut_extrusion,
            "connection_test_running": self.connection_test_running,
            "tool": self.tool,
            "remaining_distance": self.extruders[self.tool].remaining_distance,
            "is_enabled": self.extruders[self.tool].is_enabled,
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