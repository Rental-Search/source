define(["angular", "eloue/modules/booking/BookingModule",
    "eloue/modules/booking/services/CallService",
    "eloue/modules/booking/services/ProductService",
    "eloue/modules/booking/services/PriceService",
    "eloue/modules/booking/services/MessageService"
], function (angular) {
    "use strict";

    angular.module("EloueApp.BookingModule").controller("ProductDetailsCtrl", ["$scope", "$route", "CallService", "ProductService", "PriceService", "MessageService", function ($scope, $route, CallService, ProductService, Priceservice, MessageService) {

        var currentDate = new Date();
        var currentDateStr = currentDate.getDate() + "/" + (currentDate.getMonth() + 1) + "/" + currentDate.getFullYear();
        $scope.productId = $route.current.params.productId;
        $scope.bookingDetails = {
            "fromDate": Date.today().toString("dd/MM/yyyy hh:mm"),
            "toDate": Date.today().toString("dd/MM/yyyy hh:mm")
        };
        $scope.durationDays = 0;
        $scope.durationHours = 0;
        $scope.bookingPrice = 0;
        $scope.pricePerDay = 0;
        $scope.caution = 0;
        $scope.productRelatedMessages = {};
        $scope.ownerCallDetails = {};
        //TODO: get it from product info
        $scope.available = true;

        MessageService.getMessageThread($scope.productId).$promise.then(function (result) {
            $scope.productRelatedMessages = result.messages;
        });

        CallService.getContactCallDetails($scope.productId).$promise.then(function (result) {
            $scope.ownerCallDetails = result;
        });

        Priceservice.getPricePerDay($scope.productId).$promise.then(function (result) {
            $scope.pricePerDay = result.amount;
        });

        /**
         * Update the product booking price based on selected duration.
         */
        $scope.updatePrice = function updatePrice() {
            console.log($scope.bookingDetails.fromDate + "  " + $scope.bookingDetails.toDate);

            var fromDateTime = new Date(Date.parse($scope.bookingDetails.fromDate));
            var toDateTime = new Date(Date.parse($scope.bookingDetails.toDate));
            var duration = toDateTime.getTime() - fromDateTime.getTime();

            var x = duration / 1000;
            x /= 60;
            x /= 60;
            var hours = Math.round(x % 24);
            x /= 24;
            var days = Math.round(x);
            console.log(days + "  " + hours);
            $scope.durationDays = days;
            $scope.durationHours = hours;
            $scope.bookingPrice = ($scope.pricePerDay * ((hours / 24) + days)).toFixed(2);
        };


        $scope.shouldIndent = function shouldIndent(message, feed, first) {
            //TODO:
            return !first;
        };

        $scope.getAvatar = function getAvatar(uri) {
            //TODO:
            return 'https://s3-us-west-2.amazonaws.com/watu.io-assets/avatar_default.jpg';
        };

        $scope.callOwner = function callOwner() {
            //TODO: call real service
            console.log("Calling product owner..");
        };

        $scope.sendBookingRequest = function sendBookingRequest() {
             //TODO: call real service
            console.log("Send booking request..");
        };

        $scope.openBookingModal = function openBookingModal() {
            $('.modal').modal('hide');
            $("#bookingModal").modal("show");
        };

        $scope.openMessageModal = function openMessageModal() {
            $('.modal').modal('hide');
            $("#messageModal").modal("show");
        };

        $scope.openPhoneModal = function openPhoneModal() {
            $('.modal').modal('hide');
            $("#phoneModal").modal("show");
        };
    }]);
});