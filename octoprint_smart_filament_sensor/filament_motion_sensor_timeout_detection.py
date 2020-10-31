import RPi.GPIO as GPIO
import threading
import time

class FilamentMotionSensorTimeoutDetection(threading.Thread):
    used_pin = -1
    max_not_moving_time = -1
    lastMotion = 0
    keepRunning = True

    # Initialize FilamentMotionSensor
    def __init__(self, threadID, threadName, pMaxNotMovingTime, pLogger, pUsedPin_0=-1, pUsedPin_1=-1, pUsedPin_2=-1, pUsedPin_3=-1, pCallback=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.callback = pCallback
        self._logger = pLogger

        self.used_pin_0 = pUsedPin_0
        self.used_pin_1 = pUsedPin_1
        self.used_pin_2 = pUsedPin_2
        self.used_pin_3 = pUsedPin_3
        self.max_not_moving_time = pMaxNotMovingTime
        self.lastMotion = time.time()
        self.keepRunning = True

        if(self.used_pin_0 > 0):
            GPIO.add_event_detect(self.used_pin_0, GPIO.BOTH, callback=self.motion)

        if(self.used_pin_1 > 0):
            GPIO.add_event_detect(self.used_pin_1, GPIO.BOTH, callback=self.motion)

        if(self.used_pin_2 > 0):
            GPIO.add_event_detect(self.used_pin_2, GPIO.BOTH, callback=self.motion)
        
        if(self.used_pin_3 > 0):
            GPIO.add_event_detect(self.used_pin_3, GPIO.BOTH, callback=self.motion)

    # Override run method of threading
    def run(self):
        while self.keepRunning:
            timespan = (time.time() - self.lastMotion)

            if (timespan > self.max_not_moving_time):
                if(self.callback != None):
                    self.callback()

            time.sleep(0.250)

        if(self.used_pin_0 > 0):
            GPIO.remove_event_detect(self.used_pin_0)

        if(self.used_pin_1 > 0):
            GPIO.remove_event_detect(self.used_pin_1)

        if(self.used_pin_2 > 0):
            GPIO.remove_event_detect(self.used_pin_2)
        
        if(self.used_pin_3 > 0):
            GPIO.remove_event_detect(self.used_pin_3)

    # Eventhandler for GPIO filament sensor signal
    # The new state of the GPIO pin is read and determinated.
    # It is checked if motion is detected and printed to the console.
    def motion(self, pPin):
        self.lastMotion = time.time()
        self._logger.debug("Motion detected at " + str(self.lastMotion))