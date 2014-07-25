define(["angular",
    "eloue/services/ProductService",
    "eloue/services/PriceService",
    "eloue/services/MessageService",
    "eloue/services/UserService",
    "eloue/constants"
], function (angular) {
    "use strict";

    angular.module("EloueApp").controller("ProductDetailsCtrl", ["$scope", "$route", "ProductService", "PriceService", "MessageService", "UserService", "Endpoints", function ($scope, $route, ProductService, PriceService, MessageService, UserService, Endpoints) {

        //TODO: change to real user ID and product ID
        $scope.currentUserId = 17506;
        $scope.productId = 315;
        $scope.bookingDetails = {
            "fromDate": Date.today().add(1).days().toString("dd/MM/yyyy"),
            "fromHour": "08:00:00",
            "toDate": Date.today().add(2).days().toString("dd/MM/yyyy"),
            "toHour": "08:00:00"
        };
        $scope.duration = "0 jour";
        $scope.bookingPrice = 0;
        $scope.pricePerDay = 0;
        $scope.caution = 0;
        $scope.productRelatedMessages = [];
        $scope.ownerCallDetails = {};
        //TODO: get it from product info
        $scope.available = true;
        $scope.newMessage = {};
        $scope.hours = [
            {"label": "00h", "value": "00:00:00"},
            {"label": "01h", "value": "01:00:00"},
            {"label": "02h", "value": "02:00:00"},
            {"label": "03h", "value": "03:00:00"},
            {"label": "04h", "value": "04:00:00"},
            {"label": "05h", "value": "05:00:00"},
            {"label": "06h", "value": "06:00:00"},
            {"label": "07h", "value": "07:00:00"},
            {"label": "08h", "value": "08:00:00"},
            {"label": "09h", "value": "09:00:00"},
            {"label": "10h", "value": "10:00:00"},
            {"label": "11h", "value": "11:00:00"},
            {"label": "12h", "value": "12:00:00"},
            {"label": "13h", "value": "13:00:00"},
            {"label": "14h", "value": "14:00:00"},
            {"label": "15h", "value": "15:00:00"},
            {"label": "16h", "value": "16:00:00"},
            {"label": "17h", "value": "17:00:00"},
            {"label": "18h", "value": "18:00:00"},
            {"label": "19h", "value": "19:00:00"},
            {"label": "20h", "value": "20:00:00"},
            {"label": "21h", "value": "21:00:00"},
            {"label": "22h", "value": "22:00:00"},
            {"label": "23h", "value": "23:00:00"}
        ];

        UserService.getUser($scope.currentUserId).$promise.then(function (result) {
            $scope.currentUser = result;
        });

        ProductService.getProduct($scope.productId).then(function (result) {
            $scope.product = result;
            $scope.ownerCallDetails = {
                number: result.phone.number,
                tariff: "0.15"
            };
        });

        MessageService.getMessageThread($scope.productId).then(function (result) {
            angular.forEach(result, function(value, key) {
                var senderId = $scope.getIdFromUrl(value.sender);
                UserService.getUser(senderId).$promise.then(function (result) {
                    value.sender = result;
                });
            });
            $scope.productRelatedMessages = result;
        });

        PriceService.getPricePerDay($scope.productId).$promise.then(function (result) {
            if (result.results && result.results.length > 0) {
                $scope.pricePerDay = result.results[0].amount;
            } else {
                $scope.pricePerDay = 0;
            }
        });

        /**
         * Update the product booking price based on selected duration.
         */
        $scope.updatePrice = function updatePrice() {
            var fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour;
            var toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour;

            var fromDateTime = new Date(Date.parse(fromDateTimeStr));
            var toDateTime = new Date(Date.parse(toDateTimeStr));
            var today = Date.today().set({hour: 8, minute: 0});
            if (fromDateTime > toDateTime) {
               $scope.dateRangeError = "From date cannot be after to date";
            } else if (fromDateTime < today) {
               $scope.dateRangeError = "From date cannot be before today";
            } else {
                ProductService.isAvailable($scope.productId, fromDateTimeStr, toDateTimeStr, "1").$promise.then(function (result) {
                    $scope.duration = result.duration;
                    $scope.pricePerDay = result.unit_value;
                    $scope.bookingPrice = result.total_price;
                    $scope.available = result.max_available > 0;
                });
            }
        };

        $scope.sendMessage = function sendMessage() {
            var message = $scope.newMessage;
            message.sender = Endpoints.api_url + "users/" + $scope.currentUser.id + "/";
            message.recipient = Endpoints.api_url + "users/" + $scope.product.owner.id + "/";
            message.sent_at = new Date().toString("yyyy-MM-ddTHH:mm:ss");
            if ($scope.productRelatedMessages && $scope.productRelatedMessages.length > 0) {
                message.thread = $scope.productRelatedMessages[$scope.productRelatedMessages.length - 1].thread;
            }

            MessageService.sendMessage(message, $scope.productId).then(function (result) {
                $scope.productRelatedMessages.push(result);
                $scope.newMessage = {};
            });
        };

        $scope.shouldIndent = function shouldIndent(message, feed, first) {
            //TODO:
            return !first;
        };

        $scope.getAvatar = function getAvatar(uri) {
            return uri ? uri : 'img/avatar_default.jpg';
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
        };

        $scope.getIdFromUrl = function getIdFromUrl(url) {
            return url.slice(0, url.length - 1).substring(url.slice(0, url.length - 1).lastIndexOf("/") + 1, url.length);
        };

        $scope.updatePrice();
    }]);
});