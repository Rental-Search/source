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
        function ($scope, $stateParams, $q, $window, $timeout, Endpoints, MessageThreadsService, BookingsService, ProductRelatedMessagesService, ProductsService, UtilsService) {

            $scope.items = [];

            $scope.lazyLoadConfig = {
                resultField: 'results',
                // Inverse messages list.
                inverse: true,
                // Set custom target name to not cause affecting threads list.
                loadingTarget: 'Messages'
            };

            $scope.handleResponseErrors = function (error, object, action) {
                $scope.submitInProgress = false;
                $scope.showNotification(object, action, false);
            };

            $scope.$watch('items', function(newValue, oldValue) {
                // On first page loaded scroll list to the bottom.
                if (oldValue.length == 0 && newValue.length != 0) {
                    $scope.scrollMessagesListToBottom();
                }
                if ($scope.messageThread) {
                    UtilsService.updateMessagesSender($scope.items, $scope.messageThread.sender, $scope.currentUser);
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
                if (!$scope.messageThread.last_message.read_at && (UtilsService.getIdFromUrl($scope.messageThread.last_message.recipient) == results.currentUser.id)) {
                    $("#thread-" + $scope.messageThread.id).find(".unread-marker").hide();
                    ProductRelatedMessagesService.markAsRead($scope.messageThread.last_message.id);
                }

                if ($scope.messageThread.product) {

                    // Get booking product
                    BookingsService.getBookingByProduct($scope.messageThread.product.id).then(function (booking) {
                        if (!booking) {
                            // Options for the select element
                            $scope.availableHours = [
                                {"label": "00.00", "value": "00:00:00"},
                                {"label": "01.00", "value": "01:00:00"},
                                {"label": "02.00", "value": "02:00:00"},
                                {"label": "03.00", "value": "03:00:00"},
                                {"label": "04.00", "value": "04:00:00"},
                                {"label": "05.00", "value": "05:00:00"},
                                {"label": "06.00", "value": "06:00:00"},
                                {"label": "07.00", "value": "07:00:00"},
                                {"label": "08.00", "value": "08:00:00"},
                                {"label": "09.00", "value": "09:00:00"},
                                {"label": "10.00", "value": "10:00:00"},
                                {"label": "11.00", "value": "11:00:00"},
                                {"label": "12.00", "value": "12:00:00"},
                                {"label": "13.00", "value": "13:00:00"},
                                {"label": "14.00", "value": "14:00:00"},
                                {"label": "15.00", "value": "15:00:00"},
                                {"label": "16.00", "value": "16:00:00"},
                                {"label": "17.00", "value": "17:00:00"},
                                {"label": "18.00", "value": "18:00:00"},
                                {"label": "19.00", "value": "19:00:00"},
                                {"label": "20.00", "value": "20:00:00"},
                                {"label": "21.00", "value": "21:00:00"},
                                {"label": "22.00", "value": "22:00:00"},
                                {"label": "23.00", "value": "23:00:00"}
                            ];

                            $scope.newBooking = {
                                start_date: Date.today().add(1).days().toString("dd/MM/yyyy"),
                                end_date: Date.today().add(2).days().toString("dd/MM/yyyy"),
                                start_time: $scope.availableHours[0],
                                end_time: $scope.availableHours[0]
                            };

                            $scope.requestBooking = function () {
                                $scope.submitInProgress = true;
                                //Get product details
                                ProductsService.getAbsoluteUrl($scope.messageThread.product.id).then(function (result) {
                                    $window.location.href = result.url + "#/booking";
                                }, function (error) {
                                    $scope.handleResponseErrors(error, "booking", "redirect");
                                });
                            };
                            $scope.booking = booking;
                            $scope.updateNewBookingInfo();
                        } else {
                            $scope.booking = booking;
                            $scope.allowDownloadContract = $.inArray($scope.booking.state, ["pending", "ongoing", "ended", "incident", "closed"]) !== -1;
                            $scope.contractLink = Endpoints.api_url + "bookings/" + $scope.booking.uuid + "/contract/";
                        }
                    }, function (reason) {
                        console.log(reason);
                    });
                }
                // Get users' roles
                var usersRoles = MessageThreadsService.getUsersRoles($scope.messageThread, results.currentUser.id);

                // Post new message
                $scope.postNewMessage = function () {
                    $scope.submitInProgress = true;
                    ProductRelatedMessagesService.postMessage($stateParams.id, usersRoles.senderId, usersRoles.recipientId,
                        $scope.message, null, $scope.messageThread.product.id).then(
                        function (data) {
                            // Clear message field
                            $scope.message = "";

                            // Add new message.
                            $scope.items.push(data);
                            $scope.submitInProgress = false;
                            $scope.showNotification("message", "send", true);


                        }, function(error) {
                            $scope.handleResponseErrors(error, "message", "send");
                        }
                    );
                };

                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            };

            $scope.updateNewBookingInfo = function () {
                var fromDateTimeStr = $scope.newBooking.start_date + " " + $scope.newBooking.start_time.value,
                    toDateTimeStr = $scope.newBooking.end_date + " " + $scope.newBooking.end_time.value,
                    fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss"),
                    toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");

                ProductsService.isAvailable($scope.messageThread.product.id,
                    fromDateTimeStr, toDateTimeStr, 1).then(
                    function (data) {
                        $scope.parseProductAvailabilityResponse(data, fromDateTime, toDateTime);
                    },
                    function (error) {
                        $scope.handleResponseErrors(error, "booking", "update");
                    }
                );
            };

            $scope.parseProductAvailabilityResponse = function (data, fromDateTime, toDateTime) {
                var period = UtilsService.calculatePeriodBetweenDates(fromDateTime.toString(), toDateTime.toString());
                // Set data for displaying
                $scope.newBooking.period_days = period.period_days;
                $scope.newBooking.period_hours = period.period_hours;
                $scope.newBooking.total_amount = data.total_price;
                // Set data for request
                $scope.newBooking.started_at = fromDateTime.toString("yyyy-MM-ddThh:mm:ss");
                $scope.newBooking.ended_at = toDateTime.toString("yyyy-MM-ddThh:mm:ss");
                $scope.newBooking.borrower = Endpoints.api_url + "users/" + $scope.currentUser.id + "/";
                $scope.newBooking.product = Endpoints.api_url + "products/" + $scope.messageThread.product.id + "/";
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
            }
        }
    ]);
});
