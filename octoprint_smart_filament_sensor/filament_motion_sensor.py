import RPi.GPIO as GPIO
import threading
import time

class FilamentMotionSensor(threading.Thread):
    used_pin = -1
    max_not_moving_time = -1
    lastMotion = 0
    keepRunning = True

    # Initialize FilamentMotionSensor
    def __init__(self, threadID, threadName, pUsedPin, pMaxNotMovingTime, pGPIO, pLogger, pCallback=None):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = threadName
        self.callback = pCallback
        self._logger = pLogger

        self.used_pin = pUsedPin
        self.max_not_moving_time = pMaxNotMovingTime
        self.lastMotion = time.time()
        self.keepRunning = True
        self.setupGPIO(self.motion, pGPIO)

    # Override run method of threading
    def run(self):
        #print("Starting Thread: " + self.name) 
        while self.keepRunning:
            timespan = (time.time() - self.lastMotion)

            if (timespan > self.max_not_moving_time):
                if(self.callback != None):
                    #self.callback(False)
                    self.callback()
            #else:
                #if(self.callback != None):
                    #self.callback(True)

            time.sleep(0.250)
        
        GPIO.cleanup()
        #print ("Stop thread: " + self.name)

    # Initialize GPIO pin
    def setupGPIO(self, pCallback, pGPIO):
        if pGPIO == 0:
            self._logger.info("Using Board Mode")
            GPIO.setmode(GPIO.BOARD)
        else:
            self._logger.info("Using BCM Mode")
            GPIO.setmode(GPIO.BCM)

        # Set up the GPIO channels - one input and one output
        GPIO.setup(self.used_pin, GPIO.IN)
        # Add GPIO event detection and callback handler
        GPIO.add_event_detect(self.used_pin, GPIO.BOTH, callback=pCallback)

    # Eventhandler for GPIO filament sensor signal
    # The new state of the GPIO pin is read and determinated.
    # It is checked if motion is detected and printed to the console.
    def motion(self, pPin):
        self.lastMotion = time.time()