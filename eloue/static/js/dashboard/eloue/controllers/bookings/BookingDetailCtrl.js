define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/BookingsService",
    "../../../../common/eloue/services/CommentsService",
    "../../../../common/eloue/services/PhoneNumbersService",
    "../../../../common/eloue/services/SinistersService",
    "../../../../common/eloue/services/UsersService",
    "../../../../common/eloue/services/ShippingsService",
    "../../../../common/eloue/services/ProductShippingPointsService",
    "../../../../common/eloue/services/PatronShippingPointsService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the booking detail page.
     */
    EloueDashboardApp.controller("BookingDetailCtrl", [
        "$scope",
        "$stateParams",
        "$window",
        "Endpoints",
        "BookingsService",
        "CommentsService",
        "PhoneNumbersService",
        "SinistersService",
        "UsersService",
        "ShippingsService",
        "ProductShippingPointsService",
        "PatronShippingPointsService",
        function ($scope, $stateParams, $window, Endpoints, BookingsService, CommentsService, PhoneNumbersService, SinistersService, UsersService, ShippingsService, ProductShippingPointsService, PatronShippingPointsService) {

            // Initial comment data
            $scope.comment = {rate: 0};
            $scope.showIncidentForm = false;
            $scope.showIncidentDescription = false;
            $scope.userInfo = {};

            /**
             * On rating star click
             * @param star star icon index
             */
            $scope.starClicked = function (star) {
                $scope.comment.rate = star;
            };

            // Load booking details
            BookingsService.getBookingDetails($stateParams.uuid).then(function (bookingDetails) {
                $scope.applyBookingDetails(bookingDetails);
            });

            $scope.applyBookingDetails = function (bookingDetails) {
                console.log(bookingDetails);
                $scope.bookingDetails = bookingDetails;
                $scope.allowDownloadContract = $.inArray($scope.bookingDetails.state, ["pending", "ongoing", "ended", "incident", "closed"]) !== -1;
                $scope.showIncidentDescription = $scope.bookingDetails.state === "incident";
                if (!$scope.currentUserPromise) {
                    $scope.currentUserPromise = UsersService.getMe();
                }
                $scope.currentUserPromise.then(function (currentUser) {
                    $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";
                    $scope.contractLink = Endpoints.api_url + "bookings/" + $stateParams.uuid + "/contract/";
                    $scope.isOwner = $scope.currentUserUrl.indexOf(bookingDetails.owner.id) !== -1;
                    $scope.isBorrower = $scope.currentUserUrl.indexOf(bookingDetails.borrower.id) !== -1;
                    var borrower = bookingDetails.borrower, owner = bookingDetails.owner;

                    $scope.borrowerName = borrower.username;
                    $scope.borrowerSlug = borrower.slug;
                    if ($scope.isOwner) {
                        $scope.loadUserInfo(borrower);
                        $scope.loadPhoneNumber(borrower.default_number);
                    }
                    $scope.ownerName = owner.username;
                    $scope.ownerSlug = owner.slug;
                    if ($scope.isBorrower) {
                        $scope.loadUserInfo(owner);
                        $scope.loadPhoneNumber(owner.default_number);
                    }
                });

                $scope.markListItemAsSelected("booking-", $stateParams.uuid);
                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
                // Load comments
                CommentsService.getCommentList($stateParams.uuid).then(function (commentList) {
                    $scope.commentList = commentList;
                    $scope.showCommentForm = $scope.commentList.length === 0 && $scope.bookingDetails.state === "ended";
                });

                if ($scope.showIncidentDescription) {
                    SinistersService.getSinisterList($stateParams.uuid).then(function (sinisterList) {
                        if (sinisterList.results) {
                            $scope.sinister = sinisterList.results[0];
                        }
                    });
                }
                if ($scope.bookingDetails.shipping.enabled) {
                    $scope.totalBookingPrice = Number($scope.bookingDetails.total_amount) + Number($scope.bookingDetails.shipping.price);
                    console.log($scope.bookingDetails.shipping);
                    $scope.searchShippingPointsInProgres = true;
                    ProductShippingPointsService.getByProduct($scope.bookingDetails.product.id).then(function (productShippingPointData) {
                        //Show shipping choice only if there are existing product shipping points
                        if (!!productShippingPointData.results && productShippingPointData.results.length > 0) {
                            if ($scope.isOwner) {
                                $scope.departure_point = productShippingPointData.results[0];
                            } else {
                                $scope.arrival_point = productShippingPointData.results[0];
                            }
                            PatronShippingPointsService.getByPatronAndBooking($scope.bookingDetails.borrower.id, $stateParams.uuid).then(function (patronShippingPointData) {
                                if (!!patronShippingPointData.results && patronShippingPointData.results.length > 0) {
                                    if ($scope.isOwner) {
                                        $scope.arrival_point = patronShippingPointData.results[0];
                                    } else {
                                        $scope.departure_point = patronShippingPointData.results[0];
                                    }
                                    $scope.searchShippingPointsInProgres = false;
                                }
                            }, function (error) {
                                $scope.handleResponseErrors(error, "shipping_point", "get");
                            });
                        }
                    }, function (error) {
                        $scope.handleResponseErrors(error, "shipping_point", "get");
                    });
                    ShippingsService.getByBooking($stateParams.uuid).then(function (shippingList) {
                        if (!!shippingList.results && shippingList.results.length > 0) {
                            $scope.shipping = shippingList.results[0];
                            $scope.voucherLink = Endpoints.api_url + "shippings/" + $scope.shipping.id + "/document/";
                        }
                    });
                }
            };

            $scope.loadPhoneNumber = function (phoneObj) {
                if (phoneObj) {
                    if ($scope.showRealPhoneNumber($scope.bookingDetails.state)) {
                        $scope.phoneNumber = phoneObj.number.numero || phoneObj.number;
                    } else {
                        PhoneNumbersService.getPremiumRateNumber(phoneObj.id).then(function (result) {
                            if (!result.error || result.error === "0") {
                                $scope.phoneNumber = result.numero;
                            }
                        });
                    }
                }
            };

            $scope.loadUserInfo = function (userObj) {
                $scope.userInfo = userObj;
                UsersService.getStatistics(userObj.id).then(function (stats) {
                    if (!stats.booking_comments_count) {
                        stats.booking_comments_count = 0;
                    }
                    if (!stats.bookings_count) {
                        stats.bookings_count = 0;
                    }
                    $scope.userInfo.stats = stats;
                });
            };

            $scope.downloadContract = function () {
                BookingsService.downloadContract($stateParams.uuid);
            };

            $scope.downloadVoucher = function () {
                ShippingsService.downloadVoucher($scope.shipping.id, $scope.isOwner);
            };

            /**
             * Show real number of the owner if the booking have the pending status and after.
             * @param status booking status
             * @returns show be real number shown
             */
            $scope.showRealPhoneNumber = function (status) {
                return $.inArray(status, ["pending", "ongoing", "ended", "incident", "refunded", "closed"]) !== -1;
            };

            $scope.handleResponseErrors = function (error, object, action) {
                $scope.serverError = error.errors;
                $scope.submitInProgress = false;
                $scope.resetActionsProgress();
                $scope.searchShippingPointsInProgres = false;
                $scope.showNotification(object, action, false);
            };

            $scope.acceptBooking = function () {
                $scope.submitInProgress = true;
                $scope.acceptingInProgress = true;
                BookingsService.acceptBooking($stateParams.uuid).then(
                    $scope.processAcceptBookingResponse,
                    function (error) {
                        $scope.handleResponseErrors(error, "booking", "accept");
                    }
                );
            };

            $scope.processAcceptBookingResponse = function () {
                if ($scope.bookingDetails.shipping.enabled) {
                    ProductShippingPointsService.getByProduct($scope.bookingDetails.product.id).then(
                        $scope.processProductShippingPointsResponse,
                        function (error) {
                            $scope.handleResponseErrors(error, "booking", "accept");
                        }
                    );
                } else {
                    $scope.showNotification("booking", "accept", true);
                    $window.location.reload();
                }
            };

            $scope.processProductShippingPointsResponse = function (productShippingPointData) {
                //Show shipping choice only if there are existing product shipping points
                if (!!productShippingPointData.results && productShippingPointData.results.length > 0) {
                    var productShippingPoint = productShippingPointData.results[0];
                    PatronShippingPointsService.getByPatronAndBooking($scope.bookingDetails.borrower.id, $stateParams.uuid).then(
                        function(patronShippingPointData) {
                            $scope.processPatronShippingPointsResponse(patronShippingPointData, productShippingPoint);
                        },
                        function (error) {
                            $scope.handleResponseErrors(error, "booking", "accept");
                        }
                    );
                } else {
                    $scope.showNotification("booking", "accept", true);
                    $window.location.reload();
                }
            };

            $scope.processPatronShippingPointsResponse = function (patronShippingPointData, productShippingPoint) {
                if (!!patronShippingPointData.results && patronShippingPointData.results.length > 0) {
                    var patronShippingPoint = patronShippingPointData.results[0], shipping;
                    // TODO: Price is hardcoded for now, will be taken from some third-party pricing service
                    shipping = {
                        price: "10.0",
                        booking: Endpoints.api_url + "bookings/" + $scope.bookingDetails.uuid + "/",
                        departure_point: Endpoints.api_url + "productshippingpoints/" + productShippingPoint.id + "/",
                        arrival_point: Endpoints.api_url + "patronshippingpoints/" + patronShippingPoint.id + "/"
                    };
                    ShippingsService.saveShipping(shipping).then(function () {
                        $scope.showNotification("shipping", "save", true);
                        $window.location.reload();
                    }, function (error) {
                        $scope.handleResponseErrors(error, "booking", "accept");
                    });
                } else {
                    $scope.showNotification("booking", "accept", true);
                    $window.location.reload();
                }
            };

            $scope.rejectBooking = function () {
                $scope.submitInProgress = true;
                $scope.rejectingInProgress = true;
                BookingsService.rejectBooking($stateParams.uuid).then(function () {
                    $scope.showNotification("booking", "reject", true);
                    $window.location.reload();
                }, function (error) {
                    $scope.handleResponseErrors(error, "booking", "reject");
                });
            };

            $scope.showCancelConfirm = function () {
                $("#confirm").modal();
            };

            $scope.cancelBooking = function () {
                $scope.submitInProgress = true;
                $scope.cancellingInProgress = true;
                BookingsService.cancelBooking($stateParams.uuid).then(function () {
                    $scope.showNotification("booking", "cancel", true);
                    $window.location.reload();
                }, function (error) {
                    $scope.handleResponseErrors(error, "booking", "cancel");
                });
            };

            $scope.declareIncident = function () {
                $scope.showIncidentForm = true;
            };

            // Method to post new comment
            $scope.postComment = function () {
                $scope.submitInProgress = true;
                CommentsService.postComment($stateParams.uuid, $scope.comment.text, $scope.comment.rate).then(
                    function () {
                        $scope.showNotification("comment", "post", true);
                        $scope.showCommentForm = false;
                        $scope.submitInProgress = false;
                    },
                    function (error) {
                        $scope.handleResponseErrors(error, "comment", "post");
                    }
                );
            };

            // Method to post new incident
            $scope.postIncident = function () {
                $scope.submitInProgress = true;
                BookingsService.postIncident($stateParams.uuid, $scope.incident.description).then(
                    function () {
                        $scope.showNotification("sinister", "post", true);
                        $scope.showIncidentForm = false;
                        $window.location.reload();
                    },
                    function (error) {
                        $scope.handleResponseErrors(error, "sinister", "post");
                    }
                );
            };

            // Reset all actions progress such as rejecting, accepting or canceling reservation to disable
            // spinner over the href.
            $scope.resetActionsProgress = function () {
                $scope.rejectingInProgress = false;
                $scope.acceptingInProgress = false;
                $scope.cancellingInProgress = false;
            };
        }
    ]);
});
