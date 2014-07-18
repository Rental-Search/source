define(["angular", "eloue/modules/booking/BookingModule",
    "eloue/modules/booking/services/CallService",
    "eloue/modules/booking/services/ProductService",
    "eloue/modules/booking/services/PriceService",
    "eloue/modules/booking/services/MessageService",
    "eloue/services"
], function (angular) {
    "use strict";

    angular.module("EloueApp.BookingModule").controller("ProductDetailsCtrl", ["$scope", "$route", "CallService", "ProductService", "PriceService", "MessageService", function ($scope, $route, CallService, ProductService, PriceService, MessageService) {

        //TODO: change to real service
        $scope.currentUser = {
            "id": 1190,
            "email": "1190@e-loue.cc",
            "company_name": "fdsfds",
            "is_professional": false,
            "slug": "benoit",
            "avatar": "pictures/avatars/a1fc68d292034f45b9ce559bb88d9bec.jpg",
            "default_address": "http://10.0.0.111:8000/api/2.0/addresses/18/",
            "default_number": "http://10.0.0.111:8000/api/2.0/phonenumbers/18/",
            "about": "",
            "work": "",
            "school": "",
            "hobby": "",
            "languages": [],
            "drivers_license_date": null,
            "drivers_license_number": "",
            "date_of_birth": null,
            "place_of_birth": "",
            "rib": "",
            "url": ""
        };
        $scope.productId = $route.current.params.productId;
        $scope.bookingDetails = {
            "fromDate": Date.today().add(1).days().toString("dd/MM/yyyy hh:mm"),
            "toDate": Date.today().add(2).days().toString("dd/MM/yyyy hh:mm")
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
        $scope.newMessage = {};

        ProductService.getProduct($scope.productId).$promise.then(function (result) {
            $scope.product = result;
        });

        MessageService.getMessageThread($scope.productId).$promise.then(function (result) {
            $scope.productRelatedMessages = result.messages;
        });

        CallService.getContactCallDetails($scope.productId).$promise.then(function (result) {
            $scope.ownerCallDetails = result;
        });

        PriceService.getPricePerDay($scope.productId).$promise.then(function (result) {
            $scope.pricePerDay = result.amount;
        });

        /**
         * Update the product booking price based on selected duration.
         */
        $scope.updatePrice = function updatePrice() {


            var fromDateTime = new Date(Date.parse($scope.bookingDetails.fromDate));
            var toDateTime = new Date(Date.parse($scope.bookingDetails.toDate));
            var duration = toDateTime.getTime() - fromDateTime.getTime();
            var x = duration / 1000;
            x /= 60;
            x /= 60;
            var hours = Math.round(x % 24);
            x /= 24;
            var days = Math.round(x);
            $scope.durationDays = days;
            $scope.durationHours = hours;
            $scope.bookingPrice = ($scope.pricePerDay * ((hours / 24) + days)).toFixed(2);
        };

        $scope.sendMessage = function sendMessage() {
            var message = $scope.newMessage;
            message.sender = $scope.currentUser;
            message.timestamp = new Date().getTime();
            $scope.productRelatedMessages.push(message);
            //TODO: save message

            $scope.newMessage = {};
        };

        $scope.shouldIndent = function shouldIndent(message, feed, first) {
            //TODO:
            return !first;
        };

        $scope.getAvatar = function getAvatar(uri) {
            return uri ? uri  : 'images/avatar_default.jpg';
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
            $scope.openModal("bookingModal");
        };

        $scope.openMessageModal = function openMessageModal() {
            $scope.openModal("messageModal");
        };

        $scope.openPhoneModal = function openPhoneModal() {
            $scope.openModal("phoneModal");
        };

        $scope.openModal = function openModal(modalId) {
            $('.modal').modal('hide');
            $("#" + modalId).modal("show");
        }
    }]);
});