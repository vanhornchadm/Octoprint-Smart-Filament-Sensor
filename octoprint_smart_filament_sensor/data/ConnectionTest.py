from octoprint_smart_filament_sensor.filament_motion_sensor_timeout_detection import FilamentMotionSensorTimeoutDetection

class ConnectionTest(object):
    @property
    def connectionTestThread(self):
        return self._connectionTestThread

    @connectionTestThread.setter
    def connectionTestThread(self, value):
        self._connectionTestThread = value

    def __init__(self, pLogger, pCallback=None):
        self._connectionTestThread = None
        self._logger = pLogger
        self.callbackConnectionTest = pCallback
    
    # Connection tests
    def stop_connection_test(self):
        if (self._connectionTestThread is not None and self._connectionTestThread.name == "ConnectionTest"):
            self._connectionTestThread.keepRunning = False
            self._connectionTestThread = None
            #self._data.connection_test_running = False
            self._logger.info("Connection test stopped")
        else:
            self._logger.info("Connection test is not running")

        return True # Stopped successfully

    def start_connection_test(self, pPin):
        CONNECTION_TEST_TIME = 2
        if(self._connectionTestThread == None):
            #TODO hard coded pin
            self._connectionTestThread = FilamentMotionSensorTimeoutDetection(1, "ConnectionTest", pPin, 
                CONNECTION_TEST_TIME, self._logger, pCallback=self.callbackConnectionTest)
            self._connectionTestThread.start()
            #self._data.connection_test_running = True
            self._logger.info("Connection test started")

            return True # Started successfully
        else:
            return False # Problems starting