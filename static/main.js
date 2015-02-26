(function () {

 'use strict';

 angular.module('easytrans', [])

 .controller('easytransController', ['$scope', '$log', '$http', '$timeout',
   function($scope, $log, $http, $timeout) {

   // initialize the select option elements   
   $scope.input_preset = "fast";
   $scope.input_resolution = "1280x720"; 
   $scope.input_framerate = "30";  
   $scope.input_codec = "libx264"; 
   $scope.input_bitrate = "3000k";
   $scope.getResults = function() {

   $log.log("test");

   // fire the API request
   $http.post('/start', {"url": $scope.input_url, "preset": $scope.input_preset, "codec": $scope.input_codec, "resolution": $scope.input_resolution, "framerate": $scope.input_framerate, "bitrate": $scope.input_bitrate}).
   success(function(results) {
     $log.log(results);
     getMesurments(results);

     }).
   error(function(error) {
     $log.log(error);
     });

   };

   function getMesurments(jobID) {

     var timeout = "";
     var prices = [{"Company":"Amazon", "Calculated":"2.80", "Real":"2.60"}, {"Company":"Zencoder", "Calculated":"5.80", "Real":"5.60"},{"Company":"Encoding", "Calculated":"4.80", "Real":"4.60"},{"Company":"Uencode", "Calculated":"2.80", "Real":"2.75"}];   
     var mesurments = [{"Type":"time", "Estimate":"2.80", "Real":"2.60"}, {"Type":"price", "Estimate":"5.80", "Real":"5.60"},{"Type":"size", "Estimate":"50MB", "Real":"40MB"},{"Type":"quality", "Estimate":"0", "Real":"0.85"}];   

     var poller = function() {
       // fire another request
       $http.get('/results/'+jobID).
	 success(function(data, status, headers, config) {
	     if(status === 202) {
	     $log.log(data, status);
	     } else if (status === 200){
	     $log.log(data);

	     //time
	     mesurments[0].Estimate = Math.round(data.estimated_time * 1000000) / 1000000;
	     mesurments[0].Real = Math.round(data.real_time * 1000000) / 1000000;
	     //price (m3.xlarge	 4vCPU	13ECU	15GiB	2 x 40 SSD GB	$0.280 per Hour)
	     //price (t2.micro	1	Variable	1	EBS Only	$0.013 per Hour)
             mesurments[1].Estimate = Math.round(data.estimated_size * (0.280/3600) * 1000000) / 1000000;
	     mesurments[1].Real = Math.round(data.real_size * (0.280 / 3600) * 1000000) / 1000000;
             //size
	     mesurments[2].Estimate = data.estimated_size;
	     mesurments[2].Real = data.real_size;
	     //quality 
	     //mesurments[3].Estimate = data.Estimated;
	     //mesurments[3].Real = data.Real;
	     $scope.mesurments = mesurments;

             //compitator prices 
             prices[0].Calculated = Math.round((data.duration / 60) * 0.034 * 1000000) / 1000000; 
             prices[0].Real = Math.round((data.duration / 60) * 0.034 * 1000000) / 1000000; 
             prices[1].Calculated = Math.round((data.duration / 60) * 0.010 *1000000) / 1000000; 
             prices[1].Real = Math.round((data.duration / 60) * 0.010 * 1000000) / 1000000; 
             prices[2].Calculated = Math.round(((data.real_size / (1024)) * 2) * 1000000) / 1000000; 
             prices[2].Real = Math.round(((data.real_size / (1024)) * 2) * 1000000) / 1000000; 
             prices[3].Calculated = Math.round(((data.real_size / (1024)) * .9) * 1000000) / 1000000; 
             prices[3].Real = Math.round(((data.real_size / (1024)) * .9) * 1000000) / 1000000;  

	     $scope.prices = prices; 
	     $timeout.cancel(timeout);
	     return false;
	     }
	     // continue to call the poller() function every 2 seconds
	     // until the timeout is cancelled
	     timeout = $timeout(poller, 2000);
	     });
     };
     poller();
   }

   }

]);

}());
