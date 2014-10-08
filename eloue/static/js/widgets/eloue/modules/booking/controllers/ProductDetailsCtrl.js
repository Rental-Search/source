define(["angular", "eloue/modules/booking/BookingModule",
    "../../../../../common/eloue/values",
    "../../../../../common/eloue/services"
], function (angular) {
    "use strict";

    angular.module("EloueApp.BookingModule").controller("ProductDetailsCtrl", [
        "$scope",
        "$window",
        "$location",
        "Endpoints",
        "CivilityChoices",
        "ProductsLoadService",
        "MessageThreadsService",
        "ProductRelatedMessagesLoadService",
        "UsersService",
        "AuthService",
        "CreditCardsService",
        "BookingsLoadService",
        "BookingsService",
        function ($scope, $window, $location, Endpoints, CivilityChoices, ProductsLoadService, MessageThreadsService, ProductRelatedMessagesLoadService, UsersService, AuthService, CreditCardsService, BookingsLoadService, BookingsService) {

            $scope.creditCard = {
                id: null,
                card_number: "",
                expires: "",
                holder: "",
                masked_number: "",
                cvv: "",
                keep: "",
                holder_name: "",
                subscriber_reference: ""
            };
            $scope.newCreditCard = true;
            $scope.showSaveCard = true;
            $scope.selectedMonthAndYear = Date.today().getMonth() + " " + Date.today().getFullYear();
            $scope.showUnavailable = true;
            $scope.showBookings = true;
            $scope.bookings = [];
            $scope.currentBookings = [];
            $scope.weeks = {};
            var months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

            $scope.monthOptions = [
                {name: months[Date.today().add(-1).months().getMonth()] + " " + Date.today().add(-1).months().getFullYear(), value: Date.today().add(-1).months().getMonth() + " " + Date.today().add(-1).months().getFullYear()},
                {name: months[Date.today().getMonth()] + " " + Date.today().getFullYear(), value: Date.today().getMonth() + " " + Date.today().getFullYear()},
                {name: months[Date.today().add(1).months().getMonth()] + " " + Date.today().add(1).months().getFullYear(), value: Date.today().add(1).months().getMonth() + " " + Date.today().add(1).months().getFullYear()},
                {name: months[Date.today().add(2).months().getMonth()] + " " + Date.today().add(2).months().getFullYear(), value: Date.today().add(2).months().getMonth() + " " + Date.today().add(2).months().getFullYear()},
                {name: months[Date.today().add(3).months().getMonth()] + " " + Date.today().add(3).months().getFullYear(), value: Date.today().add(3).months().getMonth() + " " + Date.today().add(3).months().getFullYear()},
                {name: months[Date.today().add(4).months().getMonth()] + " " + Date.today().add(4).months().getFullYear(), value: Date.today().add(4).months().getMonth() + " " + Date.today().add(4).months().getFullYear()},
                {name: months[Date.today().add(5).months().getMonth()] + " " + Date.today().add(5).months().getFullYear(), value: Date.today().add(5).months().getMonth() + " " + Date.today().add(5).months().getFullYear()},
                {name: months[Date.today().add(6).months().getMonth()] + " " + Date.today().add(6).months().getFullYear(), value: Date.today().add(6).months().getMonth() + " " + Date.today().add(6).months().getFullYear()},
                {name: months[Date.today().add(7).months().getMonth()] + " " + Date.today().add(7).months().getFullYear(), value: Date.today().add(7).months().getMonth() + " " + Date.today().add(7).months().getFullYear()},
                {name: months[Date.today().add(8).months().getMonth()] + " " + Date.today().add(8).months().getFullYear(), value: Date.today().add(8).months().getMonth() + " " + Date.today().add(8).months().getFullYear()},
                {name: months[Date.today().add(9).months().getMonth()] + " " + Date.today().add(9).months().getFullYear(), value: Date.today().add(9).months().getMonth() + " " + Date.today().add(9).months().getFullYear()},
                {name: months[Date.today().add(10).months().getMonth()] + " " + Date.today().add(10).months().getFullYear(), value: Date.today().add(10).months().getMonth() + " " + Date.today().add(10).months().getFullYear()},
                {name: months[Date.today().add(11).months().getMonth()] + " " + Date.today().add(11).months().getFullYear(), value: Date.today().add(11).months().getMonth() + " " + Date.today().add(11).months().getFullYear()},
                {name: months[Date.today().add(12).months().getMonth()] + " " + Date.today().add(12).months().getFullYear(), value: Date.today().add(12).months().getMonth() + " " + Date.today().add(12).months().getFullYear()}
            ];

            // Read authorization token
            $scope.currentUserToken = AuthService.getCookie("user_token");

            if (!!$scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe().$promise;
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    $scope.loadCreditCards();
                });
            }

            $scope.getProductIdFromUrl = function () {
                var href = $window.location.href;
                href = href.substr(href.lastIndexOf("location/") + 8);
                var parts = href.split("/");
                var productId = parts[4];
                $scope.rootCategory = parts[1];
                return productId.substr(productId.lastIndexOf("-") + 1);
            };
            $scope.productId = $scope.getProductIdFromUrl();

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
            $scope.available = true;
            $scope.newMessage = {};
            $scope.threadId = null;
            $scope.civilityOptions = CivilityChoices;
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

            ProductsLoadService.getProduct($scope.productId, true, true).then(function (result) {
                $scope.product = result;
                //TODO: owner contact details will be defined in some other way.
                $scope.ownerCallDetails = {
                    number: result.phone.number.numero,
                    tariff: result.phone.number.tarif
                };
                $scope.loadCalendar();
            });

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
                    $scope.dateRangeError = null;
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
                ProductRelatedMessagesLoadService.postMessage($scope.threadId, $scope.currentUser.id, $scope.product.owner.id,
                    $scope.newMessage.body, null, $scope.product.id).then(function (result) {
                        // Clear message field
                        $scope.newMessage = {};
                        $scope.productRelatedMessages.push(result);
                    });
            };

            /**
             * Get avatar url or default url if user has no avatar.
             * @param uri
             */
            $scope.getAvatar = function getAvatar(uri) {
                return uri ? uri : '/static/img/profile_img.png';
            };

            $scope.getProductImg = function (uri) {
                return uri ? uri : '/static/img/product_img.png';
            };

            $scope.callOwner = function callOwner() {
                //TODO: call real service
                console.log("Calling product owner..");
            };

            $scope.sendBookingRequest = function sendBookingRequest() {
                // Update user info
                //TODO: patch more fields
                var userPatch = {};
                userPatch.first_name = $scope.currentUser.first_name;
                userPatch.last_name = $scope.currentUser.last_name;
                UsersService.updateUser(userPatch).$promise.then(function (result) {
                    // Update credit card info
                    $scope.creditCard.expires = $scope.creditCard.expires.replace("/", "");
                    if ($scope.creditCard.masked_number == "") {
                        if (!!$scope.creditCard.id) {
                            CreditCardsService.deleteCard($scope.creditCard).$promise.then(function (result) {
                                CreditCardsService.saveCard($scope.creditCard).$promise.then(function (result) {
                                    $scope.requestBooking();
                                });
                            });
                        } else {
                            CreditCardsService.saveCard($scope.creditCard).$promise.then(function (result) {
                                $scope.requestBooking();
                            });
                        }
                    } else {
                        $scope.requestBooking();
                    }
                });
            };

            $scope.requestBooking = function () {
                var booking = {};
                var fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour;
                var toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour;
                var fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                var toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                booking.started_at = fromDateTime.toString("yyyy-MM-ddTHH:mm");
                booking.ended_at = toDateTime.toString("yyyy-MM-ddTHH:mm");
                booking.owner = Endpoints.api_url + "users/" + $scope.product.owner.id + "/";
                booking.borrower = Endpoints.api_url + "users/" + $scope.currentUser.id + "/";
                booking.product = Endpoints.api_url + "products/" + $scope.product.id + "/";
                // Create booking
                BookingsLoadService.requestBooking(booking).then(
                    function (booking) {
                        var paymentInfo = {};
                        if ($scope.creditCard.card_number && $scope.creditCard.cvv) {
                            paymentInfo = {
                                card_number: $scope.creditCard.card_number,
                                expires: $scope.creditCard.expires,
                                cvv: $scope.creditCard.cvv,
                                holder_name: $scope.creditCard.holder_name
                            };
                        }else {
                            // send only credit card link if using saved credit card
                            paymentInfo = {
                                credit_card: Endpoints.api_url + "credit_cards/" + $scope.creditCard.id + "/"
                            };
                        }

                        BookingsLoadService.payForBooking(booking.uuid, paymentInfo).then(function (result) {
                            $(".modal").modal("hide");
                        });
                    }
                );
            };

            $scope.clearCreditCard = function () {
                $scope.newCreditCard = true;
                $scope.creditCard = {
                    id: $scope.creditCard.id,
                    card_number: "",
                    expires: "",
                    holder: "",
                    masked_number: "",
                    cvv: "",
                    keep: "",
                    holder_name: "",
                    subscriber_reference: ""
                };
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

            /**
             * Load necessary data on modal window open event based on modal name.
             */
            $scope.$on("openModal", function (event, args) {
                if ((args.name === "message") && $scope.productRelatedMessages.length == 0) {
                    $scope.loadMessageThread();
                } else if (args.name === "booking") {
                    $scope.loadCreditCards();
                }
            });

            /**
             * Restore path when closing modal window.
             */
            $scope.$on("closeModal", function (event, args) {
                var currentPath = $location.path();
                var newPath = currentPath.slice(0, currentPath.indexOf(args.name));
                $location.path(newPath);
                $scope.$apply();
            });

            $scope.loadCreditCards = function () {
                if ($scope.currentUser) {
                    CreditCardsService.getCardsByHolder($scope.currentUser.id).then(function (result) {
                        var cards = result.results;
                        if (!!cards && cards.length > 0) {
                            $scope.creditCard = cards[0];
                            $scope.creditCard.expires = $scope.creditCard.expires.slice(0, 2) + "/" + $scope.creditCard.expires.slice(2);
                            $scope.newCreditCard = false;
                        }
                    });
                }
            };

            $scope.isAuto = function () {
                return ($scope.rootCategory === "automobile");
            };

            $scope.loadMessageThread = function () {
                MessageThreadsService.getMessageThread($scope.productId, $scope.currentUser.id).then(function (result) {
                    angular.forEach(result, function (value, key) {
                        $scope.threadId = value.id;
                        var senderId = $scope.getIdFromUrl(value.sender);
                        UsersService.get(senderId).$promise.then(function (result) {
                            value.sender = result;
                        });
                    });
                    $scope.loadMessageThread();
                });
            };

            $scope.loadCalendar = function () {
                BookingsService.getBookingsByProduct($scope.product.id).then(function (bookings) {

                    angular.forEach(bookings, function (value, key) {
                        value.startDay = Date.parse(value.start_date.day + " " + value.start_date.month + " " + value.start_date.year);
                        value.endDay = Date.parse(value.end_date.day + " " + value.end_date.month + " " + value.end_date.year);
                    });
                    $scope.bookings = bookings;

                    $scope.updateCalendar();
                });
            };

            $scope.updateCalendar = function () {
                $scope.currentBookings = [];
                var s = $scope.selectedMonthAndYear.split(" ");
                var date = new Date();
                date.setMonth(s[0]);
                date.setFullYear(s[1]);
                var weeks = [];
                var start = new Date(date.moveToFirstDayOfMonth());
                for (var i = 0; i < 6; i++) {
                    var currentDay = start.moveToDayOfWeek(1, -1);
                    var days = [];
                    for (var j = 0; j < 7; j++) {
                        var isBooked = false;
                        angular.forEach($scope.bookings, function (value, key) {
                            if (currentDay.between(value.startDay, value.endDay)) {
                                isBooked = true;
                                $scope.currentBookings.push(value);
                            }
                        });

                        days.push({dayOfMonth: currentDay.getDate(), isBooked: isBooked});
                        currentDay.add(1).days();
                    }

                    var week = {};
                    week.weekDays = days;
                    weeks.push(week);
                    start.add(1).weeks();
                }
                $scope.weeks = weeks;
            };

            $scope.onShowUnavailable = function () {
                //TODO: implement when product availability is added to the model
            };

            $scope.onShowBookings = function () {
                console.log("onShowBookings");
            };

            $scope.selectTab = function(tabName) {
                $('[id^=tabs-]').each(function () {
                    var item = $(this);
                    if (("#" + item.attr("id")) == tabName) {
//                        item.show();
                        item.removeClass("ng-hide");
                    } else {
//                        item.hide();
                        item.addClass("ng-hide");
                    }
                });
                $('a[href^=#tabs-]').each(function () {
                    var item = $(this);
                    if (item.attr("href") == tabName) {
                        item.addClass("current");
                    } else {
                        item.removeClass("current");
                    }
                });
            };

            $scope.selectTab("#tabs-photos");
        }]);
});