define(["angular", "eloue/modules/booking/BookingModule",
    "eloue/modules/booking/services/MessageService",
    "../../../../../common/eloue/values",
    "../../../../../common/eloue/services"
], function (angular) {
    "use strict";

    angular.module("EloueApp.BookingModule").controller("ProductDetailsCtrl", ["$scope", "$route", "$location", "ProductsLoadService", "MessageService", "UsersService", "AuthService", "Endpoints", function ($scope, $route, $location, ProductsLoadService, MessageService, UsersService, AuthService, Endpoints) {

        // Read authorization token
        $scope.currentUserToken = AuthService.getCookie("user_token");

        if (!!$scope.currentUserToken) {
            // Get current user
            $scope.currentUserPromise = UsersService.getMe().$promise;
            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
            });
        }
        //TODO: change to real product ID
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


        /**
         * Update the product booking price based on selected duration.
         */
        $scope.updatePrice = function updatePrice() {
            var fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour;
            var toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour;
            var fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss");
            var toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");
            var today = Date.today().set({hour: 8, minute: 0});
            if (fromDateTime > toDateTime) {
                $scope.dateRangeError = "From date cannot be after to date";
            } else if (fromDateTime < today) {
                $scope.dateRangeError = "From date cannot be before today";
            } else {
                ProductsLoadService.isAvailable($scope.productId, fromDateTimeStr, toDateTimeStr, "1").then(function (result) {
                    $scope.duration = result.duration;
                    $scope.pricePerDay = result.unit_value;
                    $scope.bookingPrice = result.total_price;
                    $scope.available = result.max_available > 0;
                });
            }
        };

        /**
         * Send new message to the owner.
         */
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

        /**
         * Checks if message in message thread should have an indent on the page.
         */
        $scope.shouldIndent = function shouldIndent(message, feed, first) {
            //TODO:
            return !first;
        };

        /**
         * Get avatar url or default url if user has no avatar.
         * @param uri
         */
        $scope.getAvatar = function getAvatar(uri) {
            return uri ? uri : '/static/img/avatar_default.jpg';
        };

        $scope.callOwner = function callOwner() {
            //TODO: call real service
            console.log("Calling product owner..");
        };

        $scope.sendBookingRequest = function sendBookingRequest() {
            //TODO: call real service
            console.log("Send booking request..");
        };

        /**
         * Retrieves identifier of the object from provided url, that ends with "../{%ID%}/"
         * @param url URL
         * @returns ID
         */
        $scope.getIdFromUrl = function getIdFromUrl(url) {
            return url.slice(0, url.length - 1).substring(url.slice(0, url.length - 1).lastIndexOf("/") + 1, url.length);
        };

        $scope.updatePrice();

        /**
         * Catch "redirectToLogin" event
         */
        $scope.$on("redirectToLogin", function () {
            $location.path("/login");
        });

        $scope.$on("openModal", function (event, args) {
            if ((args.name === "message") && $scope.productRelatedMessages.length == 0) {
                $scope.loadMessageThread();
            }
            if (!$scope.product) {
                $scope.loadProductDetails();
            }
        });

        $scope.loadMessageThread = function () {
            MessageService.getMessageThread($scope.productId).then(function (result) {
                angular.forEach(result, function (value, key) {
                    var senderId = $scope.getIdFromUrl(value.sender);
                    UsersService.get(senderId).$promise.then(function (result) {
                        value.sender = result;
                    });
                });
                $scope.productRelatedMessages = result;
            });
        };

        $scope.loadProductDetails = function () {
            ProductsLoadService.getProduct($scope.productId, true, true, true, false).then(function (result) {
                $scope.product = result;
                //TODO: owner contact details will be defined in some other way.
                $scope.ownerCallDetails = {
                    number: result.phone.number,
                    tariff: "0.15"
                };
            });
        }
    }]);
});