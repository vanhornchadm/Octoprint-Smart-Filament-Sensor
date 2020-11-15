$(function(){
    function SmartFilamentSensorSettingsViewModel(parameters){
        var self = this;

        self.settingsViewModel = parameters[0];

        // Initialize Attributes
        self.boardMode = ko.observable();
        self.detectionMethod = ko.observable();
        self.pauseCommand = ko.observable();
        self.motionSensorPin = ko.observable();
        self.motionSensorEnabled = ko.observable();
        self.timeoutDetectionTime = ko.observable();
        self.distanceDetectionDistance = ko.observable();

        // Load from Settings
        self.loadSettings = function(){
            self.boardMode(self.settingsViewModel.settings.plugins.smartfilamentsensor.mode());
            self.detectionMethod(self.settingsViewModel.settings.plugins.smartfilamentsensor.detection_method());
            self.pauseCommand(self.settingsViewModel.settings.plugins.smartfilamentsensor.pause_command());
            self.motionSensorPin(self.settingsViewModel.settings.plugins.smartfilamentsensor.motion_sensor_pin());
            self.motionSensorEnabled(self.settingsViewModel.settings.plugins.smartfilamentsensor.motion_sensor_enabled());
            self.timeoutDetectionTime(self.settingsViewModel.settings.plugins.smartfilamentsensor.motion_sensor_max_not_moving());
            self.distanceDetectionDistance(self.settingsViewModel.settings.plugins.smartfilamentsensor.motion_sensor_detection_distance());
        };

        self.onSettingsShown = function() {
            self.loadSettings();
        };

        self.onSettingsBeforeSave = function(){
            var data = {
                plugins: {
                    smartfilamentsensor: {
                        mode: self.boardMode(),
                        detection_method: self.detectionMethod(),
                        pause_command: self.pauseCommand(),
                        motion_sensor_pin: self.motionSensorPin(),
                        motion_sensor_enabled: self.motionSensorEnabled(),
                        motion_sensor_max_not_moving: self.timeoutDetectionTime(),
                        motion_sensor_detection_distance: self.distanceDetectionDistance(),
                    }
                }
            };

            self.settingsViewModel.saveData(data);
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: SmartFilamentSensorSettingsViewModel,
        name: "smartFilamentSensorSettingsViewModel",
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_smartfilamentsensor"]
    });
});
