$(function(){
    function SmartFilamentSensorSettingsViewModel(parameters){
        var self = this;

        self.settingsViewModel = parameters[0];
        self.printerStateViewModel = parameters[1];
        self.connectionTestDialog = undefined;

        self.remainingDistance = ko.observable(undefined);
        self.lastMotionDetected = ko.observable(undefined);
        self.isFilamentMoving = ko.observable(undefined);
        self.isConnectionTestRunning = ko.observable(false);
        self.gpioPinConnectionTest = ko.observable(undefined);

        self.onStartup = function() {
            self.connectionTestDialog = $("#settings_plugin_smartfilamentsensor_connectiontest");

            /*if(self.settingsViewModel.extruders.length == 0){
                self.addExtruder();
            }*/
        };
        
        self.showConnectionTest = function() {
            self.connectionTestDialog.modal({
                show: true
            });
        };

        self.onDataUpdaterPluginMessage = function(plugin, data){
            if(plugin !== "smartfilamentsensor"){
                return;
            }
            
            var message = JSON.parse(data);
            self.remainingDistance(message["remaining_distance"]);
            self.lastMotionDetected(message["last_motion_detected"]);
            self.isConnectionTestRunning(message["connection_test_running"]);
            self.gpioPinConnectionTest(message["gpio_pin_connection_test"]);

            if(message["filament_moving"] == true){
                self.isFilamentMoving("Yes, filament is moving");
            }
            else{
                self.isFilamentMoving("No, filament is not moving");
            }
        };

        self.enableConnectionTest = ko.pureComputed(function() {
            return !self.printerStateViewModel.isBusy();
        });

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

        self.addExtruder = function(){
			self.settingsViewModel.settings.plugins.smartfilamentsensor.extruders.push({'pin':ko.observable(-1),'isEnabled':ko.observable(false)});
		}

        self.removeExtruder = function(data){
			self.settingsViewModel.settings.plugins.smartfilamentsensor.extruders.remove(data);			
		}
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: SmartFilamentSensorSettingsViewModel,
        name: "smartFilamentSensorSettingsViewModel",
        dependencies: ["settingsViewModel", "printerStateViewModel"],
        elements: ["#settings_plugin_smartfilamentsensor"]
    });
});
