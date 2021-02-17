#### Raspberry ####
import RPi.GPIO as GPIO

class ISfsExtruder(object):
    # The GPIO pin of the sensor
    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        self._pin = value
        self.cbRefreshUI(self)

    # Enables or disables the sensor
    @property
    def is_enabled(self):
        return self._is_enabled

    @is_enabled.setter
    def is_enabled(self, value):
        self._is_enabled = value
        self.cbRefreshUI(self)

    # The last status of the filament
    @property
    def filament_moving(self):
        return self._filament_moving

    @filament_moving.setter
    def filament_moving(self, value):
        self._logger.debug("New value filament_moving %r" % (value))
        self._filament_moving = value
        self.cbRefreshUI(self)

#### Timeout detection ####
    # The last point in time the extruder moved
    #@property
    #def last_motion_detected(self):
    #    return self._last_motion_detected

    #@last_motion_detected.setter
    #def last_motion_detected(self, value):
    #    self._last_motion_detected = value
    #    self.cbRefreshUI(self)

#### Events ####
    @property
    def cbRefreshUI(self):
        return self._cbRefreshUI

    @cbRefreshUI.setter
    def cbRefreshUI(self, value):
        self._cbRefreshUI = value

    @property
    def cbFilamentStopped(self):
        return self._cbFilamentStopped

    @cbFilamentStopped.setter
    def cbFilamentStopped(self, value):
        self._cbFilamentStopped = value

#### Print ####
    @property
    def absolut_extrusion(self):
        return self._absolut_extrusion

    @absolut_extrusion.setter
    def absolut_extrusion(self, value):
        self._absolut_extrusion = value

#### Initialisation ####
    def __init__(self, pLogger, pPin, pSensorEnabled, pCbStoppedMoving=None, pCbRefreshUI=None):
        self._logger = pLogger
        self._pin = int(pPin)
        self._is_enabled = pSensorEnabled
        self._cbFilamentStopped = pCbStoppedMoving
        self._cbRefreshUI = pCbRefreshUI
                
        self._absolut_extrusion = False
        self._filament_moving = False

    def init_gpio_pin(self):
        GPIO.setup(self.pin, GPIO.IN)
        self._logger.info("Setup input pin: %r" % (self.pin))

#### Extrusion ####
    def filament_moved(self, pCurrentE=None):
        pass

    def gpio_event(self, pPin):
        pass

#### Sensor ####
    def start_sensor(self):
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self.gpio_event)
        pass

    def stop_sensor(self):
        pass

#### Conversion ####
    def ToYAML(self):
        data = {
            'pin': self.pin,
            'isEnabled': self.is_enabled
        }

        return data

    def ToJSON(self):
        pass
