define(["angular-mocks", "eloue/controllers/bookings/BookingDetailCtrl"], function () {

    describe("Controller: BookingDetailCtrl", function () {

        var BookingDetailCtrl,
            scope, stateParams, window, endpointsMock, bookingsLoadServiceMock, commentsLoadServiceMock, phoneNumbersServiceMock,
            sinistersServiceMock, usersServiceMock, shippingsServiceMock,
            productShippingPointsServiceMock, patronShippingPointsServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            endpointsMock = {
                api_url: "/api/2.0/"
            };

            bookingsLoadServiceMock = {
                getBookingDetails: function (bookingUUID) {
                    console.log("bookingsLoadServiceMock:getBookingDetails called with bookingUUID = " + bookingUUID);
                    return {
                        then: function () {
                            return {response: {}}
                        }
                    }
                },
                downloadContract: function (uuid) {
                    return null;
                },
                acceptBooking: function (uuid) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },
                rejectBooking: function (uuid) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },
                cancelBooking: function (uuid) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },
                postIncident: function (uuid, description) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                }
            };
            commentsLoadServiceMock = {
                getCommentList: function (bookingUUID) {
                    console.log("commentsLoadServiceMock:getCommentList called with bookingUUID = " + bookingUUID);
                    return {
                        then: function () {
                            return {response: {}}
                        }
                    }
                },
                postComment: function (bookingUUID, comment, rate) {
                    console.log("commentsLoadServiceMock:postComment called with bookingUUID = " + bookingUUID + ", comment = " + comment + ", rate = " + rate);
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                }
            };

            phoneNumbersServiceMock = {
                getPremiumRateNumber: function (phoneId) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                }
            };

            sinistersServiceMock = {
                getSinisterList: function (uuid) {
                    return {
                        then: function () {
                            return {result: {}}
                        }
                    }
                }
            };

            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },

                getStatistics: function (userId) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                }
            };

            shippingsServiceMock = {
                getByBooking: function (uuid) {
                    return {
                        then: function () {
                            return {result: {}}
                        }
                    }
                },
                downloadVoucher: function (shippingId, isOwner) {
                    return null;
                },
                saveShipping: function (shipping) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                }
            };

            productShippingPointsServiceMock = {
                getByProduct: function () {
                    return {
                        then: function (productId) {
                            return {result: {}}
                        }
                    }
                }
            };

            patronShippingPointsServiceMock = {
                getByPatronAndBooking: function (borrowerId, uuid) {
                    return {
                        then: function () {
                            return {result: {}}
                        }
                    }
                }
            };

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("BookingsLoadService", bookingsLoadServiceMock);
                $provide.value("CommentsLoadService", commentsLoadServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("SinistersService", sinistersServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("ShippingsService", shippingsServiceMock);
                $provide.value("ProductShippingPointsService", productShippingPointsServiceMock);
                $provide.value("PatronShippingPointsService", patronShippingPointsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.showNotification = function(object, action, bool){};
            stateParams = {};
            spyOn(bookingsLoadServiceMock, "getBookingDetails").and.callThrough();
            spyOn(bookingsLoadServiceMock, "downloadContract").and.callThrough();
            spyOn(bookingsLoadServiceMock, "acceptBooking").and.callThrough();
            spyOn(bookingsLoadServiceMock, "rejectBooking").and.callThrough();
            spyOn(bookingsLoadServiceMock, "cancelBooking").and.callThrough();
            spyOn(bookingsLoadServiceMock, "postIncident").and.callThrough();
            spyOn(commentsLoadServiceMock, "getCommentList").and.callThrough();
            spyOn(commentsLoadServiceMock, "postComment").and.callThrough();
            spyOn(phoneNumbersServiceMock, "getPremiumRateNumber").and.callThrough();
            spyOn(sinistersServiceMock, "getSinisterList").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(usersServiceMock, "getStatistics").and.callThrough();
            spyOn(shippingsServiceMock, "getByBooking").and.callThrough();
            spyOn(shippingsServiceMock, "downloadVoucher").and.callThrough();
            spyOn(shippingsServiceMock, "saveShipping").and.callThrough();
            spyOn(productShippingPointsServiceMock, "getByProduct").and.callThrough();
            spyOn(patronShippingPointsServiceMock, "getByPatronAndBooking").and.callThrough();

            BookingDetailCtrl = $controller('BookingDetailCtrl', {
                $scope: scope,
                $stateParams: stateParams,
                $window: window,
                Endpoints: endpointsMock,
                BookingsLoadService: bookingsLoadServiceMock,
                CommentsLoadService: commentsLoadServiceMock,
                PhoneNumbersService: phoneNumbersServiceMock,
                SinistersService: sinistersServiceMock,
                UsersService: usersServiceMock,
                ShippingsService: shippingsServiceMock,
                ProductShippingPointsService: productShippingPointsServiceMock,
                PatronShippingPointsService: patronShippingPointsServiceMock
            });
            expect(bookingsLoadServiceMock.getBookingDetails).toHaveBeenCalled();
        }));

        it("BookingDetailCtrl should be not null", function () {
            expect(!!BookingDetailCtrl).toBe(true);
        });

        it("BookingDetailCtrl:postComment", function () {
            stateParams.uuid = 1;
            scope.comment = {
                text: 'text',
                rate: 1
            };
            scope.postComment();
            expect(commentsLoadServiceMock.postComment).toHaveBeenCalledWith(stateParams.uuid, scope.comment.text, scope.comment.rate);
        });

        it("BookingDetailCtrl:starClicked", function () {
            scope.starClicked();
        });

        it("BookingDetailCtrl:loadPhoneNumber", function () {
            scope.loadPhoneNumber();
        });

        it("BookingDetailCtrl:loadUserInfo", function () {
            var userObj = {
                id: 1
            };
            scope.loadUserInfo(userObj);
        });

        it("BookingDetailCtrl:downloadContract", function () {
            scope.downloadContract();
        });

        it("BookingDetailCtrl:downloadVoucher", function () {
            scope.shipping = {
                id: 1
            };
            scope.downloadVoucher();
        });

        it("BookingDetailCtrl:showRealPhoneNumber", function () {
            scope.showRealPhoneNumber();
        });

        it("BookingDetailCtrl:handleResponseErrors", function () {
            var error = {
                errors: {}
            };
            scope.handleResponseErrors(error);
        });

        it("BookingDetailCtrl:acceptBooking", function () {
            scope.acceptBooking();
        });

        it("BookingDetailCtrl:rejectBooking", function () {
            scope.rejectBooking();
        });

        it("BookingDetailCtrl:cancelBooking", function () {
            scope.cancelBooking();
        });

        it("BookingDetailCtrl:declareIncident", function () {
            scope.declareIncident();
        });

        it("BookingDetailCtrl:postIncident", function () {
            scope.incident = {
                description: "description"
            };
            scope.postIncident();
        });
    });
});