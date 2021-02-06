import json

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
    def absolut_extrusion(self):
        return self._absolut_extrusion

    @absolut_extrusion.setter
    def absolut_extrusion(self, value):
        self._absolut_extrusion = value

    # Is the connection test running
    @property
    def connection_test_running(self):
        return self._connection_test_running

    @connection_test_running.setter
    def connection_test_running(self, value):
        self._connection_test_running = value
        self.callbackUpdateUI()

    # Constructor
    def __init__(self, pRemainingDistance, pAbsolutExtrusion, pCallback=None):
        self._remaining_distance = pRemainingDistance
        self._absolut_extrusion = pAbsolutExtrusion
        # The START_DISTANCE_OFFSETS solves the problem of false detections after the print start
        self.START_DISTANCE_OFFSET = 7
        self.callbackUpdateUI = pCallback

        # Default values
        self._print_started = False
        self._lastE = -1
        self._currentE = -1
        self._last_motion_detected = ""
        self._filament_moving = False

    # Convert the current object into JSON
    def toJSON(self):
         return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)