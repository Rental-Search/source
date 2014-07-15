define(["angular", "eloue/modules/product_details/ProductDetailsModule",
    "eloue/modules/product_details/services/CallService",
    "eloue/modules/product_details/services/ProductService",
    "eloue/modules/product_details/services/PriceService"
], function (angular) {
    "use strict";

    angular.module("EloueApp.ProductDetailsModule").controller("ProductDetailsCtrl", ["$scope", "$route", "CallService", "ProductService", "PriceService", function ($scope, $route, CallService, ProductService, Priceservice) {

        var currentDate = new Date();
        var currentDateStr = currentDate.getDate() + "/" + (currentDate.getMonth() +1) + "/" + currentDate.getFullYear();
        $scope.productId = $route.current.params.productId;
        $scope.bookingDetails = {
            "fromDate": currentDateStr,
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
            var fromDateTime = new Date();
            var toDateTime = new Date();
            var duration = fromDateTime.getTime() - fromDateTime.getTime();

        };

        $scope.getCallDetails = function getPhoneNumber() {
            //TODO: get owner id by product id
            var ownerId = 1;
            $scope.ownerCallDetails = CallService.getContactCallDetails(ownerId);
        }
    }]);
});