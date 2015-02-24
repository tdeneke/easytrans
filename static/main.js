(function () {

 'use strict';

 angular.module('WordcountApp', [])

 .controller('WordcountController', ['$scope', '$log', '$http', '$timeout',
	 function($scope, $log, $http, $timeout) {

         // initialize the select option elements   
         $scope.input_preset = "fast";
         $scope.input_resolution = "1280x720"; 
	 $scope.input_framerate = "30";  
         $scope.input_codec = "h264"; 
         $scope.input_bitrate = "3000k";
         $scope.getResults = function() {

	 $log.log("test");

	 // fire the API request
	 $http.post('/start', {"url": $scope.input_url, "preset": $scope.input_preset, "codec": $scope.input_codec, "resolution": $scope.input_resolution, "framerate": $scope.input_framerate, "bitrate": $scope.input_bitrate}).
	 success(function(results) {
		 $log.log(results);
		 getWordCount(results);

		 }).
	 error(function(error) {
		 $log.log(error);
		 });

	 };

	 function getWordCount(jobID) {

		 var timeout = "";

		 var poller = function() {
			 // fire another request
			 $http.get('/results/'+jobID).
				 success(function(data, status, headers, config) {
						 if(status === 202) {
						 $log.log(data, status);
						 } else if (status === 200){
						 $log.log(data);
						 $scope.wordcounts = data;
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
