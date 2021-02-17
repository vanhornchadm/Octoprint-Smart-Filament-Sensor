import RPi.GPIO as GPIO
import threading
import time

class SfsTimeoutDetection(threading.Thread):
    used_pin = -1
    max_not_moving_time = -1
    keepRunning = True

    # Initialize FilamentMotionSensor
    def __init__(self, threadID, threadName, pUsedPin, pMaxNotMovingTime, pLogger, pCallback=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.callbackFilamentMoving = pCallback
        self._logger = pLogger

        self.used_pin = pUsedPin
        self.max_not_moving_time = pMaxNotMovingTime
        self.last_motion_detected = time.time()
        self.keepRunning = True

        # Remove event, if already an event was set
        try:
            GPIO.remove_event_detect(self.used_pin)
        except:
            self._logger.warn("Pin " + str(pUsedPin) + " not used before")
            
        GPIO.add_event_detect(self.used_pin, GPIO.BOTH, callback=self.motion)
        self._logger.debug("Added GPIO detection to pin %r" % (self.used_pin))

    # Override run method of threading
    def run(self):
        while self.keepRunning:
            timespan = (time.time() - self.last_motion_detected)

            if (timespan > self.max_not_moving_time):
                if(self.callbackFilamentMoving != None):
                    self.callbackFilamentMoving(False, self.last_motion_detected)

            time.sleep(0.250)

        GPIO.remove_event_detect(self.used_pin)

    # Eventhandler for GPIO filament sensor signal
    # The new state of the GPIO pin is read and determinated.
    # It is checked if motion is detected and printed to the console.
    def motion(self, pPin):
        self.last_motion_detected = time.time()
        self.callbackFilamentMoving(True, self.last_motion_detected)
        self._logger.debug("Motion detected at " + str(self.last_motion_detected))