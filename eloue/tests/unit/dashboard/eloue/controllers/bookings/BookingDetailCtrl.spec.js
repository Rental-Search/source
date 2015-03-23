define(["angular-mocks", "eloue/controllers/bookings/BookingDetailCtrl"], function () {

    describe("Controller: BookingDetailCtrl", function () {

        var BookingDetailCtrl,
            scope, stateParams, window, endpointsMock, bookingsServiceMock, commentsServiceMock, phoneNumbersServiceMock,
            sinistersServiceMock, usersServiceMock, shippingsServiceMock,
            productShippingPointsServiceMock, patronShippingPointsServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            endpointsMock = {
                api_url: "/api/2.0/"
            };

            bookingsServiceMock = {
                getBookingDetails: function (bookingUUID) {
                    console.log("bookingsServiceMock:getBookingDetails called with bookingUUID = " + bookingUUID);
                    return simpleServiceResponse;
                },
                downloadContract: function (uuid) {
                    return null;
                },
                acceptBooking: function (uuid) {
                    return simpleServiceResponse;
                },
                rejectBooking: function (uuid) {
                    return simpleServiceResponse;
                },
                cancelBooking: function (uuid) {
                    return simpleServiceResponse;
                },
                postIncident: function (uuid, description) {
                    return simpleServiceResponse;
                }
            };
            commentsServiceMock = {
                getCommentList: function (bookingUUID) {
                    console.log("commentsServiceMock:getCommentList called with bookingUUID = " + bookingUUID);
                    return simpleServiceResponse;
                },
                postComment: function (bookingUUID, comment, rate) {
                    console.log("commentsServiceMock:postComment called with bookingUUID = " + bookingUUID + ", comment = " + comment + ", rate = " + rate);
                    return simpleServiceResponse;
                }
            };

            phoneNumbersServiceMock = {
                getPremiumRateNumber: function (phoneId) {
                    return simpleServiceResponse;
                }
            };

            sinistersServiceMock = {
                getSinisterList: function (uuid) {
                    return simpleServiceResponse;
                }
            };

            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return simpleServiceResponse;
                },

                getStatistics: function (userId) {
                    return simpleServiceResponse;
                }
            };

            shippingsServiceMock = {
                getByBooking: function (uuid) {
                    return simpleServiceResponse;
                },
                downloadVoucher: function (shippingId, isOwner) {
                    return null;
                },
                saveShipping: function (shipping) {
                    return simpleServiceResponse;
                }
            };

            productShippingPointsServiceMock = {
                getByProduct: function () {
                    return simpleServiceResponse;
                }
            };

            patronShippingPointsServiceMock = {
                getByPatronAndBooking: function (borrowerId, uuid) {
                    return simpleServiceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("CommentsService", commentsServiceMock);
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
            scope.markListItemAsSelected = function(){};
            scope.initCustomScrollbars = function(){};
            stateParams = {};
            spyOn(bookingsServiceMock, "getBookingDetails").and.callThrough();
            spyOn(bookingsServiceMock, "downloadContract").and.callThrough();
            spyOn(bookingsServiceMock, "acceptBooking").and.callThrough();
            spyOn(bookingsServiceMock, "rejectBooking").and.callThrough();
            spyOn(bookingsServiceMock, "cancelBooking").and.callThrough();
            spyOn(bookingsServiceMock, "postIncident").and.callThrough();
            spyOn(commentsServiceMock, "getCommentList").and.callThrough();
            spyOn(commentsServiceMock, "postComment").and.callThrough();
            spyOn(phoneNumbersServiceMock, "getPremiumRateNumber").and.callThrough();
            spyOn(sinistersServiceMock, "getSinisterList").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(usersServiceMock, "getStatistics").and.callThrough();
            spyOn(shippingsServiceMock, "getByBooking").and.callThrough();
            spyOn(shippingsServiceMock, "downloadVoucher").and.callThrough();
            spyOn(shippingsServiceMock, "saveShipping").and.callThrough();
            spyOn(productShippingPointsServiceMock, "getByProduct").and.callThrough();
            spyOn(patronShippingPointsServiceMock, "getByPatronAndBooking").and.callThrough();
            spyOn(scope, 'showNotification').and.callThrough();
            window = {location: {reload: jasmine.createSpy()}};

            BookingDetailCtrl = $controller('BookingDetailCtrl', {
                $scope: scope,
                $stateParams: stateParams,
                $window: window,
                Endpoints: endpointsMock,
                BookingsService: bookingsServiceMock,
                CommentsService: commentsServiceMock,
                PhoneNumbersService: phoneNumbersServiceMock,
                SinistersService: sinistersServiceMock,
                UsersService: usersServiceMock,
                ShippingsService: shippingsServiceMock,
                ProductShippingPointsService: productShippingPointsServiceMock,
                PatronShippingPointsService: patronShippingPointsServiceMock
            });
            expect(bookingsServiceMock.getBookingDetails).toHaveBeenCalled();
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
            expect(commentsServiceMock.postComment).toHaveBeenCalledWith(stateParams.uuid, scope.comment.text, scope.comment.rate);
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

        it("BookingDetailCtrl:applyBookingDetails", function () {
            scope.currentUserUrl = "fsdfsd";
            var bookingDetails = {
                owner: {
                    id: 1
                },
                borrower: {
                    id: 2
                },
                shipping: {
                    enabled: false
                }
            };
            scope.applyBookingDetails(bookingDetails);
            expect(scope.bookingDetails).toEqual(bookingDetails);
        });

        it("BookingDetailCtrl:processAcceptBookingResponseWithShipping", function () {
            scope.bookingDetails = {
                product: {
                    id: 1
                },
                shipping: {
                    enabled: true
                }
            };
            scope.processAcceptBookingResponse();
            expect(scope.showNotification).toHaveBeenCalled();
        });
    });
});