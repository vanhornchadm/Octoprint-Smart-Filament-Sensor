$(function(){
    function SmartFilamentSensorSidebarViewModel(parameters){
        var self = this;

        self.settingsViewModel = parameters[0];
        //self.smartfilamentsensorSettings = self.settingsViewModel.settings.plugins.smartfilamentsensor;

        self.isSensorEnabled = ko.observable("Unknown");
        self.remainingDistance = ko.observable("Unknown");
        self.lastMotionDetected = ko.observable("Unknown");

        //Returns the value in Yes/No if the Sensor is enabled 
        self.getSensorEnabledString = function(){
            var sensorEnabled = self.settingsViewModel.settings.plugins.smartfilamentsensor.motion_sensor_enabled();

            if(sensorEnabled){
                return "Yes";
            }
            else{
                return "No";
            }
        };

        // Returns the value of detection_method as string
        self.getDetectionMethodString = function(){
            var detectionMethod = self.settingsViewModel.settings.plugins.smartfilamentsensor.detection_method();

            if(detectionMethod == 0){
                return "Timeout Detection";
            }
            else if(detectionMethod == 1){
                return "Distance Detection";
            }
        };

        self.onDataUpdaterPluginMessage = function(plugin, data){
            if(plugin !== "smartfilamentsensor"){
                return;
            }
            
            var message = JSON.parse(data);
            self.remainingDistance(message["_remaining_distance"]);
            self.lastMotionDetected(message["_last_motion_detected"]);
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: SmartFilamentSensorSidebarViewModel,
        name: "smartFilamentSensorSidebarViewModel",
        dependencies: ["settingsViewModel"],
        elements: ["#sidebar_plugin_smartfilamentsensor"]
    });
})