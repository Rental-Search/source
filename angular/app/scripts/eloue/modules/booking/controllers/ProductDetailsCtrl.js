define(["angular", "eloue/modules/booking/BookingModule",
    "eloue/modules/booking/services/CallService",
    "eloue/modules/booking/services/ProductService",
    "eloue/modules/booking/services/PriceService",
    "eloue/modules/booking/services/MessageService"
], function (angular) {
    "use strict";

    angular.module("EloueApp.BookingModule").controller("ProductDetailsCtrl", ["$scope", "$route", "CallService", "ProductService", "PriceService", "MessageService", function ($scope, $route, CallService, ProductService, Priceservice, MessageService) {

        var currentDate = new Date();
        var currentDateStr = currentDate.getDate() + "/" + (currentDate.getMonth() +1) + "/" + currentDate.getFullYear();
        $scope.productId = $route.current.params.productId;
        $scope.bookingDetails = {
            "fromDate": new Date(),
            "fromHours": "0:00 AM",
            "toDate": currentDateStr,
            "toHours": "0:00 AM"
        };
        $scope.ownerCallDetails = {
            "number" : "08.99.45.65.43",
            "tariff" : "0.15"
        };
        $scope.durationDays = 0;
        $scope.durationHours = 0;
        $scope.bookingPrice = 0;
        $scope.pricePerDay = 10;
        $scope.caution = 0;
        $scope.messages = MessageService.getMessageThread($scope.productId);

        /**
         * Initialize controls.
         */
        $scope.init = function init() {
            $scope.pricePerDay = Priceservice.getPricePerDay();
        };

        /**
         * Update the product booking price based on selected duration.
         */
        $scope.updatePrice = function updatePrice() {
            console.log($scope.bookingDetails.fromDate + "  " + $scope.bookingDetails.toDate + "  " + $scope.bookingDetails.fromHours + "  " + $scope.bookingDetails.toHours);
//            $scope.productDetailsBookingForm.fromDate.$parsers.unshift(function (viewValue) {
//                console.log(viewValue);
//            });
            var fromDateTime = new Date();
            var toDateTime = new Date();
            var duration = fromDateTime.getTime() - fromDateTime.getTime();

        };

        $scope.getCallDetails = function getPhoneNumber() {
            //TODO: get owner id by product id
            var ownerId = 1;
            $scope.ownerCallDetails = CallService.getContactCallDetails(ownerId);
        };

        $scope.getMessageThread = function getMessageThread() {
            $scope.messages = MessageService.getMessageThread($scope.productId);
        }
    }]);
});