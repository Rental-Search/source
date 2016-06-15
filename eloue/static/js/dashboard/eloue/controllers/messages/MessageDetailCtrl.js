define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/MessageThreadsService",
    "../../../../common/eloue/services/BookingsService",
    "../../../../common/eloue/services/ProductRelatedMessagesService",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/UtilsService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the message detail page.
     */
    EloueDashboardApp.controller("MessageDetailCtrl", [
        "$scope",
        "$stateParams",
        "$q",
        "$window",
        "$timeout",
        "Endpoints",
        "MessageThreadsService",
        "BookingsService",
        "ProductRelatedMessagesService",
        "ProductsService",
        "UtilsService",
        "AvailableHours",
        function ($scope, $stateParams, $q, $window, $timeout, Endpoints, MessageThreadsService, BookingsService, ProductRelatedMessagesService, ProductsService, UtilsService, AvailableHours) {

            $scope.items = [];

            var dr =  UtilsService.dateRepr, di = UtilsService.dateInternal;

            $scope.lazyLoadConfig = {
                resultField: 'results',
                // Inverse messages list.
                inverse: true,
                // Set custom target name to not cause affecting threads list.
                loadingTarget: 'Messages'
            };

            $scope.isFirstLoad = true;

            $scope.handleResponseErrors = function (error, object, action) {
                $scope.messageSubmitInProgress = false;
                $scope.bookingSubmitInProgress = false;
                $scope.showNotification(object, action, false);
            };

            $scope.$watchCollection('items', function(newValue, oldValue) {
                // On first page loaded scroll list to the bottom.
                if (newValue.length != 0 && $scope.isFirstLoad) {
                    $scope.scrollMessagesListToBottom();
                    $scope.isFirstLoad = false;
                }
                if ($scope.messageThread) {
                    var replacer = $scope.messageThread.sender.id == $scope.currentUser.id ? $scope.messageThread.recipient : $scope.messageThread.sender;
                    UtilsService.updateMessagesSender($scope.items, replacer, $scope.currentUser);
                }

                var unreadMessages = UtilsService.getUnreadMessagesIds ($scope.items, $scope.currentUser);
                if (unreadMessages.length > 0) {
                    // If there are any unread messages.

                    // Mark messages as seen.
                    ProductRelatedMessagesService.markBunchAsRead(unreadMessages).then(function() {
                        $scope.updateStatistics();
                        MessageThreadsService.isThreadSeen($scope.messageThread.id).then(function(result) {
                            if (result.seen) {
                                $("#thread-" + $scope.messageThread.id).find(".unread-marker").hide();
                            }
                        });
                    });
                }
            });

            var promises = {
                currentUser: $scope.currentUserPromise,
                messageThread: MessageThreadsService.getMessageThreadById($stateParams.id)
            };

            $q.all(promises).then(function (results) {
                $scope.applyUserAndMessageThread(results);
                // Load messages first page.
                $scope.$broadcast("startLoading" + $scope.lazyLoadConfig.loadingTarget, {parameters: [$stateParams.id], shouldReloadList: true});
            });

            $scope.applyUserAndMessageThread = function (results) {
                $scope.markListItemAsSelected("thread-", $stateParams.id);
                $scope.messageThread = results.messageThread;
                $scope.currentuser = results.currentUser;

                if ($scope.messageThread.product) {

                    // Get booking product
                    BookingsService.getBookingByProduct($scope.messageThread.product.id).then(function (booking) {
                        if (!booking) {

                            if ($scope.messageThread.product.owner.id != $scope.currentUser.id) {

                                $scope.getProductUrl();

                                // Options for the select element
                                $scope.availableHours = UtilsService.choicesHours();

                                $scope.newBooking = {
                                    start_date: dr(Date.today().add(1).days().toString("dd/MM/yyyy")),
                                    end_date: dr(Date.today().add(2).days().toString("dd/MM/yyyy")),
                                    start_time: $scope.availableHours[8],
                                    end_time: $scope.availableHours[9]
                                };

                                $scope.requestBooking = function () {
                                    $scope.bookingSubmitInProgress = true;
                                    //Get product details
                                    ProductsService.getAbsoluteUrl($scope.messageThread.product.id).then(function (result) {
                                        var redirectUrl = result.url;
                                        redirectUrl += '?date_from=' + di($scope.newBooking.start_date);
                                        redirectUrl += '&date_to=' + di($scope.newBooking.end_date);
                                        redirectUrl += '&hour_from=' + $scope.newBooking.start_time.value;
                                        redirectUrl += '&hour_to=' + $scope.newBooking.end_time.value;
                                        redirectUrl += '&show_booking=true';
                                        $window.location.href = redirectUrl;
                                    }, function (error) {
                                        $scope.handleResponseErrors(error, "booking", "redirect");
                                    });
                                };
                                $scope.booking = booking;
                                $scope.available = true;
                                $scope.updateNewBookingInfo();

                                $timeout(function() {
                                    // Initiate custom scrollbars
                                    $scope.initCustomScrollbars();
                                }, 0);

                            }
                        } else {
                            $scope.booking = booking;
                            $scope.allowDownloadContract = $.inArray($scope.booking.state, ["pending", "ongoing", "ended", "incident", "closed"]) !== -1;
                            $scope.contractLink = Endpoints.api_url + "bookings/" + $scope.booking.uuid + "/contract/";
                            $scope.getProductUrl();
                        }
                    }, function (reason) {
                        console.log(reason);
                    });
                }
                // Get users' roles
                var usersRoles = MessageThreadsService.getUsersRoles($scope.messageThread, results.currentUser.id);

                // Post new message
                $scope.postNewMessage = function () {
                    $scope.messageSubmitInProgress = true;
                    ProductRelatedMessagesService.postMessage($stateParams.id, usersRoles.senderId, usersRoles.recipientId,
                        $scope.message, null, $scope.messageThread.product.id).then(
                        function (data) {
                            analytics.track("Message Replied", {
                                recipient: data.recipient
                            });
                            // Clear message field
                            $scope.message = "";

                            // Add new message.
                            $scope.items.push(data);
                            $scope.messageSubmitInProgress = false;
                            $scope.showNotification("message", "send", true);


                        }, function(error) {
                            $scope.handleResponseErrors(error, "message", "send");
                        }
                    );
                };

                // Initiate custom scrollbars
                UtilsService.initCustomScrollbars("#messages-list");
            };

            $scope.findHour = function(hourValue) {
                for (var i = 0; i < $scope.availableHours.length; i++) {
                    if ($scope.availableHours[i].value === hourValue) {
                        return $scope.availableHours[i];
                    }
                }
            };

            $scope.getProductUrl = function() {
                ProductsService.getAbsoluteUrl($scope.messageThread.product.id).then(function(result) {
                    $scope.productUrl = result.url;
                });
            };

            $scope.updateNewBookingInfo = function () {
                var fromDateTimeStr = di($scope.newBooking.start_date) + " " + $scope.newBooking.start_time.value,
                    toDateTimeStr = di($scope.newBooking.end_date) + " " + $scope.newBooking.end_time.value,
                    fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss"),
                    toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");

                if (fromDateTime > toDateTime) {
                    //When the user change the value of the "from date" and that this new date is after the "to date" so the "to date" should be update and the value should be the same of the "from date".
                    $scope.dateRangeError = "La date de début ne peut pas être après la date de fin";
                    if (fromDateTime.getHours() < 23) {
                        $scope.newBooking.end_date = dr(fromDateTime.toString("dd/MM/yyyy"));
                        $scope.newBooking.end_time = $scope.findHour(fromDateTime.add(1).hours().toString("HH:mm:ss"));
                    } else {
                        $scope.newBooking.end_date = dr(fromDateTime.add(1).days().toString("dd/MM/yyyy"));
                        $scope.newBooking.end_time = $scope.findHour(fromDateTime.add(1).hours().toString("HH:mm:ss"));
                    }

                    // Fix for very strange eloueChosen directive behaviour. Sometimes directive doesn't get fired and
                    // UI doesn't change, but scope value was changed successfully.
                    $timeout(function () {
                        $("[id=fromHour]").trigger("chosen:updated");
                        $("[id=toHour]").trigger("chosen:updated");
                    }, 0);

                    fromDateTimeStr = $scope.newBooking.start_date + " " + $scope.newBooking.start_time.value;
                    toDateTimeStr = $scope.newBooking.end_date + " " + $scope.newBooking.end_time.value;
                }

                $timeout(function() {
                    var fromDateSelector = $("input[name='fromDate']");
                    var toDateSelector = $("input[name='toDate']");
                    fromDateSelector.datepicker('setDate', $scope.newBooking.start_date);
                    toDateSelector.datepicker('setDate', $scope.newBooking.end_date);
                }, 0);


                ProductsService.isAvailable($scope.messageThread.product.id,
                    fromDateTimeStr, toDateTimeStr, 1).then(
                    function (data) {
                        $scope.parseProductAvailabilityResponse(data, fromDateTime, toDateTime);
                    },
                    function (error) {
                        $scope.available = false;
                        $scope.handleResponseErrors(error, "booking", "update");
                    }
                );
            };

            $scope.parseProductAvailabilityResponse = function (data, fromDateTime, toDateTime) {

                var price = data.total_price;
                price = price.replace("€", "").replace("\u20ac", "").replace("Eu", "").replace(",", ".").replace(" ", "");
                price = Number(price);
                $scope.duration = data.duration;
                $scope.pricePerDay = data.unit_value;
                $scope.bookingPrice = price;
                $scope.available = data.max_available > 0;
            };

            /**
             * Scroll list to the bottom.
             */
            $scope.scrollMessagesListToBottom = function() {
                $timeout(function () {
                    $("#messages-list").mCustomScrollbar("scrollTo", "bottom", {
                        scrollInertia: 0
                    });
                }, 50);
            };

            $scope.getProductPicture = function(product) {
                var result = undefined;

                if (product && product.pictures && product.pictures[0]) {
                    return product.pictures[0].image.thumbnail;
                }

                return result;
            }
        }
    ]);
});
