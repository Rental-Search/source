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
        "ProductsService",
        function ($scope, $stateParams, $window, Endpoints, BookingsService, CommentsService, PhoneNumbersService, SinistersService, UsersService, ShippingsService, ProductShippingPointsService, PatronShippingPointsService, ProductsService) {

            // Initial comment data
            $scope.comment = {rate: 0};
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
                $scope.bookingDetails = bookingDetails;
                $scope.allowDownloadContract = $.inArray($scope.bookingDetails.state, ["pending", "ongoing", "ended", "incident", "closed"]) !== -1
                	&& !bookingDetails.owner.has_pro_subscription;
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

                $scope.comment = {rate: 0};

                $scope.markListItemAsSelected("booking-", $stateParams.uuid);
                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
                // Load comments
                CommentsService.getCommentList($stateParams.uuid).then(function (commentList) {
                    $scope.commentList = commentList;
                    if (commentList.length > 0) {
                        $scope.comment = commentList[0];
                    }
                    $scope.showCommentForm = $scope.commentList.length === 0 && $scope.bookingDetails.state === "ended"
                        && !($scope.isOwner && $scope.bookingDetail.has_pro_subscription);
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
                    $scope.searchShippingPointsInProgres = true;
                    ProductShippingPointsService.getById($scope.bookingDetails.shipping.product_point).then(function (productShippingPointData) {
                        //Show shipping choice only if there are existing product shipping points
                        if (!!productShippingPointData) {
                            if ($scope.isOwner) {
                                $scope.departure_point = productShippingPointData;
                            } else {
                                $scope.arrival_point = productShippingPointData;
                            }
                            PatronShippingPointsService.getById($scope.bookingDetails.shipping.patron_point).then(function (patronShippingPointData) {
                                if (!!patronShippingPointData) {
                                    if ($scope.isOwner) {
                                        $scope.arrival_point = patronShippingPointData;
                                    } else {
                                        $scope.departure_point = patronShippingPointData;
                                    }
                                    $scope.searchShippingPointsInProgres = false;
                                }
                            }, function (error) {
                                $scope.handleResponseErrors(error, "shipping_point", "get");
                            });
                        }
                    }, function (error) {
                        if (error.code == "60100") {
                            $scope.shippingServiceError = "Désolé, il y a un problème avec le service de livraison. Pouvez-vous contacter le service client pour plus d'informations, s'il vous plaît?";
                        }
                        $scope.handleResponseErrors(error, "shipping_point", "get");
                    });
                    ShippingsService.getByBooking($stateParams.uuid).then(function (shippingList) {
                        if (!!shippingList.results && shippingList.results.length > 0) {
                            $scope.shipping = shippingList.results[0];
                            $scope.voucherLink = Endpoints.api_url + "shippings/" + $scope.shipping.id + "/document/";
                        }
                    });
                }

                ProductsService.getAbsoluteUrl($scope.bookingDetails.product.id).then(function (result) {
                    $scope.productUrl = result.url;
                });
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
                BookingsService.getBookingDetails($stateParams.uuid).then(function (booking) {
                    $scope.showNotification("booking", "accept", true);
                    $scope.segmentBookingTrackEvent('Booking Accepted', booking);
                    $scope.reloadPage();
                });
            };

            $scope.rejectBooking = function () {
                $scope.submitInProgress = true;
                $scope.rejectingInProgress = true;
                BookingsService.rejectBooking($stateParams.uuid).then(
                    $scope.processRejectBookingResponse,
                    function (error) {
                    $scope.handleResponseErrors(error, "booking", "reject");
                });
            };

            $scope.processRejectBookingResponse = function () {
                BookingsService.getBookingDetails($stateParams.uuid).then(function (booking) {
                    $scope.showNotification("booking", "reject", true);
                    $scope.segmentBookingTrackEvent('Booking Rejected', booking);
                    $scope.reloadPage();
                });
            };

            $scope.showCancelConfirm = function () {
                $("#confirm").modal();
            };

            $scope.showComment = function() {
                $("#comment-and-rank").modal();
            };

            $scope.cancelBooking = function () {
                $scope.submitInProgress = true;
                $scope.cancellingInProgress = true;
                BookingsService.cancelBooking($stateParams.uuid).then(
                    $scope.processCancelBookingResponse,
                    function (error) {
                    $scope.handleResponseErrors(error, "booking", "cancel");
                });
            };

            $scope.processCancelBookingResponse = function () {
                BookingsService.getBookingDetails($stateParams.uuid).then(function (booking) {
                    $scope.showNotification("booking", "cancel", true);
                    $scope.segmentBookingTrackEvent('Booking Canceled', booking);
                    $scope.reloadPage();
                });
            };

            $scope.declareIncident = function () {
                $("#report-incendent").modal();
            };

            // Method to post new comment
            $scope.postComment = function () {
                $scope.submitInProgress = true;
                CommentsService.postComment($stateParams.uuid, $scope.comment.text, $scope.comment.rate).then(
                    function (result) {
                        $scope.processCommentBookingResponse(result);
                    },
                    function (error) {
                        $scope.handleResponseErrors(error, "comment", "post");
                    }
                );
            };

            $scope.processCommentBookingResponse = function (result) {
                BookingsService.getBookingDetails($stateParams.uuid).then(function (booking) {
                    $("#comment-and-rank").modal("hide");
                    $scope.showNotification("comment", "post", true);
                    $scope.showCommentForm = false;
                    $scope.submitInProgress = false;
                    $scope.commentList = [result];
                    $scope.comment = result;
                    $scope.segmentBookingTrackEvent('Booking Commented', booking);
                });
            };

            // Method to post new incident
            $scope.postIncident = function () {
                $scope.submitInProgress = true;
                BookingsService.postIncident($stateParams.uuid, $scope.incident.description).then(
                    $scope.processIncidentBookingResponse,
                    function (error) {
                        $scope.handleResponseErrors(error, "sinister", "post");
                    }
                );
            };

            $scope.processIncidentBookingResponse = function () {
                BookingsService.getBookingDetails($stateParams.uuid).then(function (booking) {
                    $("#report-incendent").modal("hide");
                    $scope.showNotification("sinister", "post", true);
                    $scope.segmentBookingTrackEvent('Booking Incident Posted', booking);
                    $scope.reloadPage();
                });
            };

            // Reset all actions progress such as rejecting, accepting or canceling reservation to disable
            // spinner over the href.
            $scope.resetActionsProgress = function () {
                $scope.rejectingInProgress = false;
                $scope.acceptingInProgress = false;
                $scope.cancellingInProgress = false;
            };

            /**
             * Reload page.
             */
            $scope.reloadPage = function() {
                $window.location.reload();
            }

            /**
             * Push track event to segment.
             *
             * @param event : name of the event
             * @param booking : booking information
             */
            $scope.segmentBookingTrackEvent = function (event, booking) {
                analytics.track(event, {
                    'booking id': booking.uuid,
                    'borrower id': booking.borrower.id,
                    'owner id': booking.owner.id,
                    'category': booking.product.category.name,
                    'category slug': booking.product.category.slug,
                    'product id': booking.product.id,
                    'product summary': booking.product.summary,
                    'product pictures': booking.product.pictures.length,
                    'duration': booking.duration,
                    'start date': booking.started_at,
                    'end date': booking.ended_at,
                    'state': booking.state,
                    'total amount': booking.total_amount 
                });
            };
        }
    ]);
});
