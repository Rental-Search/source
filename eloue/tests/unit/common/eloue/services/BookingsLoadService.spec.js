define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsLoadService", function () {

        var BookingsLoadService,
            q,
            endpointsMock,
            bookingsMock,
            utilsServiceMock,
            bookingsParseServiceMock,
            messageThreadsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            endpointsMock = {};
            bookingsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                },
                save: function () {
                    return {$promise: {}}
                },
                pay: function () {
                    return {$promise: {}}
                },
                incident: function () {
                    return {$promise: {}}
                },
                accept: function () {
                    return {$promise: {}}
                },
                cancel: function () {
                    return {$promise: {}}
                },
                reject: function () {
                    return {$promise: {}}
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {

                },
                downloadPdfFile: function(url) {}
            };
            bookingsParseServiceMock = {
                parseBookingListItem: function (bookingData, productData, picturesDataArray) {

                },
                parseBooking: function (bookingDate) {

                }
            };
            messageThreadsServiceMock = {
                getMessageThread: function (productId, userId) {

                }
            };

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("Bookings", bookingsMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("BookingsParseService", bookingsParseServiceMock);
                $provide.value("MessageThreadsService", messageThreadsServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsLoadService_, $q) {
            BookingsLoadService = _BookingsLoadService_;
            q = $q;
            spyOn(bookingsMock, "get").and.callThrough();
            spyOn(bookingsMock, "save").and.callThrough();
            spyOn(bookingsMock, "pay").and.callThrough();
            spyOn(bookingsMock, "incident").and.callThrough();
            spyOn(bookingsMock, "accept").and.callThrough();
            spyOn(bookingsMock, "cancel").and.callThrough();
            spyOn(bookingsMock, "reject").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(bookingsParseServiceMock, "parseBookingListItem").and.callThrough();
            spyOn(bookingsParseServiceMock, "parseBooking").and.callThrough();
            spyOn(messageThreadsServiceMock, "getMessageThread").and.callThrough();
        }));

        it("BookingsLoadService should be not null", function () {
            expect(!!BookingsLoadService).toBe(true);
        });

        it("BookingsLoadService:getBookingList", function () {
            var author, state, borrowerId, ownerId, page;
            BookingsLoadService.getBookingList(author, state, borrowerId, ownerId, page);
        });

        it("BookingsLoadService:getBooking", function () {
            var uuid = 1;
            BookingsLoadService.getBooking(uuid);
        });

        it("BookingsLoadService:getBookingDetails", function () {
            var uuid = 1;
            BookingsLoadService.getBookingDetails(uuid);
        });

        it("BookingsLoadService:acceptBooking", function () {
            var uuid = 1;
            BookingsLoadService.acceptBooking(uuid);
        });

        it("BookingsLoadService:cancelBooking", function () {
            var uuid = 1;
            BookingsLoadService.cancelBooking(uuid)
        });

        it("BookingsLoadService:rejectBooking", function () {
            var uuid = 1;
            BookingsLoadService.rejectBooking(uuid)
        });

        it("BookingsLoadService:postIncident", function () {
            var uuid = 1, description = "";
            BookingsLoadService.postIncident(uuid, description)
        });

        it("BookingsLoadService:downloadContract", function () {
            var uuid = 1;
            BookingsLoadService.downloadContract(uuid);
        });

        it("BookingsLoadService:getBookingByProduct", function () {
            var productId = 1;
            BookingsLoadService.getBookingByProduct(productId);
        });

        it("BookingsLoadService:requestBooking", function () {
            var booking = {};
            BookingsLoadService.requestBooking(booking);
        });

        it("BookingsLoadService:payForBooking", function () {
            var uuid = 1, paymentInfo = {};
            BookingsLoadService.payForBooking(uuid, paymentInfo);
        });
    });
});