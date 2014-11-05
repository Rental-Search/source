"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the booking detail page.
     */
    angular.module("EloueDashboardApp").controller("BookingDetailCtrl", [
        "$scope",
        "$stateParams",
        "$window",
        "Endpoints",
        "BookingsLoadService",
        "CommentsLoadService",
        "PhoneNumbersService",
        "SinistersService",
        "UsersService",
        "UtilsService",
        "ShippingsService",
        "ProductShippingPointsService",
        "PatronShippingPointsService",
        function ($scope, $stateParams, $window, Endpoints, BookingsLoadService, CommentsLoadService, PhoneNumbersService, SinistersService, UsersService, UtilsService, ShippingsService, ProductShippingPointsService, PatronShippingPointsService) {

            // Initial comment data
            $scope.comment = {rate: 0};
            $scope.showIncidentForm = false;
            $scope.showIncidentDescription = false;
            $scope.userInfo = {};

            // On rating star click
            $(".star i").click(function () {
                var self = $(this);
                $scope.$apply(function () {
                    $scope.comment.rate = self.attr("rate");
                });
            });

            // Load booking details
            BookingsLoadService.getBookingDetails($stateParams.uuid).then(function (bookingDetails) {
                $scope.bookingDetails = bookingDetails;
                $scope.allowDownloadContract = $.inArray($scope.bookingDetails.state, ["pending", "ongoing", "ended", "incident", "closed"]) != -1;
                $scope.showIncidentDescription = $scope.bookingDetails.state == 'incident';
                if (!$scope.currentUserPromise) {
                    $scope.currentUserPromise = UsersService.getMe().$promise;
                }
                $scope.currentUserPromise.then(function (currentUser) {
                    $scope.currentUserUrl = Endpoints.api_url + "users/" + currentUser.id + "/";
                    $scope.contractLink = Endpoints.api_url + "bookings/" + $stateParams.uuid + "/contract/";
                    $scope.isOwner = bookingDetails.owner.indexOf($scope.currentUserUrl) != -1;
                    $scope.isBorrower = bookingDetails.borrower.indexOf($scope.currentUserUrl) != -1;
                    UsersService.get(UtilsService.getIdFromUrl(bookingDetails.borrower)).$promise.then(function (result) {
                        $scope.borrowerName = result.username;
                        $scope.borrowerSlug = result.slug;
                        if ($scope.isOwner) {
                            $scope.loadUserInfo(result);
                            $scope.loadPhoneNumber(result.default_number);
                        }
                    });
                    UsersService.get(UtilsService.getIdFromUrl(bookingDetails.owner)).$promise.then(function (result) {
                        $scope.ownerName = result.username;
                        $scope.ownerSlug = result.slug;
                        if ($scope.isBorrower) {
                            $scope.loadUserInfo(result);
                            $scope.loadPhoneNumber(result.default_number);
                        }
                    });
                });

                $scope.markListItemAsSelected("booking-", $stateParams.uuid);
                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
                // Load comments
                CommentsLoadService.getCommentList($stateParams.uuid).then(function (commentList) {
                    $scope.commentList = commentList;
                    $scope.showCommentForm = $scope.commentList.length == 0 && $scope.bookingDetails.state == "ended";
                });

                if ($scope.showIncidentDescription) {
                    SinistersService.getSinisterList($stateParams.uuid).then(function (sinisterList) {
                        if (!!sinisterList.results) {
                            $scope.sinister = sinisterList.results[0];
                        }
                    });
                }
                if ($scope.bookingDetails.with_shipping) {
                    ProductShippingPointsService.getByProduct($scope.bookingDetails.product.id).then(function (productShippingPointData) {
                        //Show shipping choice only if there are existing product shipping points
                        if (!!productShippingPointData.results && productShippingPointData.results.length > 0) {
                            $scope.departure_point = productShippingPointData.results[0];
                            PatronShippingPointsService.getByPatronAndBooking(UtilsService.getIdFromUrl($scope.bookingDetails.borrower), $stateParams.uuid).then(function (patronShippingPointData) {
                                if (!!patronShippingPointData.results && patronShippingPointData.results.length > 0) {
                                    $scope.arrival_point = patronShippingPointData.results[0];
                                }
                            }, function (error) {
                                $scope.handleResponseErrors(error);
                            });
                        }
                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    });
                    ShippingsService.getByBooking($stateParams.uuid).then(function (shippingList) {
                        if (!!shippingList.results) {
                            $scope.shipping = shippingList.results[0];
                        }
                    });
                }
            });

            $scope.loadPhoneNumber = function (phoneObj) {
                if (phoneObj) {
                    if ($scope.showRealPhoneNumber($scope.bookingDetails.state)) {
                        $scope.phoneNumber = !!phoneObj.number.numero ? phoneObj.number.numero : phoneObj.number;
                    } else {
                        PhoneNumbersService.getPremiumRateNumber(phoneObj.id).$promise.then(function (result) {
                            if (!result.error || result.error == "0") {
                                $scope.phoneNumber = result.numero;
                            }
                        });
                    }
                }
            };

            $scope.loadUserInfo = function (userObj) {
                $scope.userInfo = userObj;
                UsersService.getStatistics(userObj.id).$promise.then(function (stats) {
                    if (!stats.booking_comments_count) {
                        stats.booking_comments_count = 0;
                    }
                    if (!stats.bookings_count) {
                        stats.bookings_count = 0;
                    }
                    $scope.userInfo.stats = stats;
                });
            };

            /**
             * Show real number of the owner if the booking have the pending status and after.
             * @param status booking status
             * @returns show be real number shown
             */
            $scope.showRealPhoneNumber = function (status) {
                return $.inArray(status, ["pending", "ongoing", "ended", "incident", "refunded", "closed"]) != -1;
            };

            $scope.handleResponseErrors = function (error) {
                $scope.serverError = error.errors;
                $scope.submitInProgress = false;
            };


            $scope.acceptBooking = function () {
                $scope.submitInProgress = true;
                BookingsLoadService.acceptBooking($stateParams.uuid).$promise.then(function (result) {
                    if ($scope.bookingDetails.with_shipping) {
                        ProductShippingPointsService.getByProduct($scope.bookingDetails.product.id).then(function (productShippingPointData) {
                            //Show shipping choice only if there are existing product shipping points
                            if (!!productShippingPointData.results && productShippingPointData.results.length > 0) {
                                var productShippingPoint = productShippingPointData.results[0];
                                PatronShippingPointsService.getByPatronAndBooking(UtilsService.getIdFromUrl($scope.bookingDetails.borrower), $stateParams.uuid).then(function (patronShippingPointData) {
                                    if (!!patronShippingPointData.results && patronShippingPointData.results.length > 0) {
                                        var patronShippingPoint = patronShippingPointData.results[0];
                                        // TODO: Price is hardcoded for now, will be taken from some third-party pricing service
                                        var shipping = {
                                            price: "10.0",
                                            booking: Endpoints.api_url + "bookings/" + $scope.bookingDetails.uuid + "/",
                                            departure_point: Endpoints.api_url + "productshippingpoints/" + productShippingPoint.id + "/",
                                            arrival_point: Endpoints.api_url + "patronshippingpoints/" + patronShippingPoint.id + "/"
                                        };
                                        ShippingsService.saveShipping(shipping).$promise.then(function (result) {
                                            $scope.showNotification(result.detail);
                                            $window.location.reload();
                                        }, function (error) {
                                            $scope.handleResponseErrors(error);
                                        });
                                    } else {
                                        $scope.showNotification(patronShippingPointData.detail);
                                        $window.location.reload();
                                    }
                                }, function (error) {
                                    $scope.handleResponseErrors(error);
                                });
                            } else {
                                $scope.showNotification(productShippingPointData.detail);
                                $window.location.reload();
                            }
                        }, function (error) {
                            $scope.handleResponseErrors(error);
                        });
                    } else {
                        $scope.showNotification(result.detail);
                        $window.location.reload();
                    }
                }, function (error) {
                    $scope.handleResponseErrors(error);
                })
            };

            $scope.rejectBooking = function () {
                $scope.submitInProgress = true;
                BookingsLoadService.rejectBooking($stateParams.uuid).$promise.then(function (result) {
                    $scope.showNotification(result.detail);
                    $window.location.reload();
                })
            };

            $scope.showCancelConfirm = function () {
                $('#confirm').modal();
            };

            $scope.cancelBooking = function () {
                $scope.submitInProgress = true;
                BookingsLoadService.cancelBooking($stateParams.uuid).$promise.then(function (result) {
                    $scope.showNotification(result.detail);
                    $window.location.reload();
                })
            };

            $scope.declareIncident = function () {
                $scope.showIncidentForm = true;
            };

            // Method to post new comment
            $scope.postComment = function () {
                $scope.submitInProgress = true;
                CommentsLoadService.postComment($stateParams.uuid, $scope.comment.text, $scope.comment.rate).$promise
                    .then(function () {
                        $scope.showNotification("Posted comment");
                        $scope.showCommentForm = false;
                        $scope.submitInProgress = false;
                    });
            };

            // Method to post new incident
            $scope.postIncident = function () {
                $scope.submitInProgress = true;
                BookingsLoadService.postIncident($stateParams.uuid, $scope.incident.description).$promise
                    .then(function (result) {
                        $scope.showNotification(result.detail);
                        $scope.showIncidentForm = false;
                        $window.location.reload();
                    });
            };
        }
    ]);
});