$(function(){
    function SmartFilamentSensorSidebarViewModel(parameters){
        var self = this;

        self.settingsViewModel = parameters[0];
        //self.smartfilamentsensorSettings = self.settingsViewModel.settings.plugins.smartfilamentsensor;

        self.isSensorEnabled = ko.observable(undefined);
        self.remainingDistance = ko.observable(undefined);
        self.lastMotionDetected = ko.observable(undefined);
        self.isFilamentMoving = ko.observable(undefined);

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
            self.isFilamentMoving(message["_filament_moving"]);

            /*if(message["_filament_moving"] == true){
                self.isFilamentMoving("Yes");
            }
            else{
                self.isFilamentMoving("No");
            }*/
        };

        self.startConnectionTest = function(){
            $.ajax({
                url: API_BASEURL + "plugin/smartfilamentsensor",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({ "command": "startConnectionTest" }),
                contentType: "application/json",
                success: self.RestSuccess
            });
        };

        self.stopConnectionTest = function(){
            $.ajax({
                url: API_BASEURL + "plugin/smartfilamentsensor",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({ "command": "stopConnectionTest" }),
                contentType: "application/json",
                success: self.RestSuccess
            });
        };

        self.RestSuccess = function(response){
            return;
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: SmartFilamentSensorSidebarViewModel,
        name: "smartFilamentSensorSidebarViewModel",
        dependencies: ["settingsViewModel"],
        elements: ["#sidebar_plugin_smartfilamentsensor"]
    });
})