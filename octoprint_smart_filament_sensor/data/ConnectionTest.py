from octoprint_smart_filament_sensor.data.SfsTimeoutExtruder import SfsTimeoutExtruder

class ConnectionTest(object):
    @property
    def connectionTestThread(self):
        return self._connectionTest

    @connectionTestThread.setter
    def connectionTestThread(self, value):
        self._connectionTest = value

    def __init__(self, pLogger, pCbStoppedMoving=None, pCbRefreshUI=None):
        self._connectionTest = None
        self._logger = pLogger
        self.cbStoppedMoving = pCbStoppedMoving
        self.cbRefreshUI = pCbRefreshUI
        self._logger.info("Initialized connection test")
    
    # Connection tests
    def stop_connection_test(self):
        if (self._connectionTest is not None):
            self._connectionTest.stop_sensor()
            self._connectionTest = None
            #self._data.connection_test_running = False
            self._logger.info("Connection test stopped")
        else:
            self._logger.info("Connection test is not running")

        return True # Stopped successfully

    def start_connection_test(self, pPin):
        CONNECTION_TEST_TIME = 2
        if(self._connectionTest == None):
            self._connectionTest = SfsTimeoutExtruder(self._logger, pPin, True, pCbStoppedMoving=self.cbStoppedMoving, pCbRefreshUI=self.cbRefreshUI)
            self._connectionTest.setup(CONNECTION_TEST_TIME, False)
            self._connectionTest.start_sensor()

            self._logger.info("Connection test started")

            return True # Started successfully
        else:
            return False # Problems starting