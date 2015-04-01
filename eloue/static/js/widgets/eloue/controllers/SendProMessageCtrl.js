define([
    'eloue/app'
], function (EloueWidgetsApp) {
    'use strict';
    /**
     * Controller to manage pro shop message sending.
     */
    EloueWidgetsApp.controller('SendProMessageCtrl', [
        '$scope',
        'UsersService',
        function ($scope, UsersService) {

            $scope.message = {};
            $scope.isSent = false;

            $scope.sendMessage = function() {
                $scope.submitInProgress = true;
                UsersService.sendProMessage($scope.recipientId, $scope.message).then(function() {
                    $scope.isSent = true;
                }, function() {
                    $scope.submitInProgress = false;
                });
            };

            $scope.setUserId = function(id) {
                $scope.recipientId = id;
            }
        }]);
});