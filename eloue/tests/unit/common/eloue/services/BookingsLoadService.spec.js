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
            spyOn(utilsServiceMock, "downloadPdfFile").and.callThrough();
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
            expect(bookingsMock.get).toHaveBeenCalled();
        });

        it("BookingsLoadService:getBooking", function () {
            var uuid = 1;
            BookingsLoadService.getBooking(uuid);
            expect(bookingsMock.get).toHaveBeenCalledWith({uuid: uuid, _cache: jasmine.any(Number)});
        });

        it("BookingsLoadService:getBookingDetails", function () {
            var uuid = 1;
            BookingsLoadService.getBookingDetails(uuid);
        });

        it("BookingsLoadService:acceptBooking", function () {
            var uuid = 1;
            BookingsLoadService.acceptBooking(uuid);
            expect(bookingsMock.accept).toHaveBeenCalledWith({uuid: uuid}, {uuid: uuid});
        });

        it("BookingsLoadService:cancelBooking", function () {
            var uuid = 1;
            BookingsLoadService.cancelBooking(uuid);
            expect(bookingsMock.cancel).toHaveBeenCalledWith({uuid: uuid}, {uuid: uuid});
        });

        it("BookingsLoadService:rejectBooking", function () {
            var uuid = 1;
            BookingsLoadService.rejectBooking(uuid);
            expect(bookingsMock.reject).toHaveBeenCalledWith({uuid: uuid}, {uuid: uuid});
        });

        it("BookingsLoadService:postIncident", function () {
            var uuid = 1, description = "";
            BookingsLoadService.postIncident(uuid, description);
            expect(bookingsMock.incident).toHaveBeenCalledWith({uuid: uuid}, {description: description});
        });

        it("BookingsLoadService:downloadContract", function () {
            var uuid = 1;
            BookingsLoadService.downloadContract(uuid);
            expect(utilsServiceMock.downloadPdfFile).toHaveBeenCalled();
        });

        it("BookingsLoadService:getBookingByProduct", function () {
            var productId = 1;
            BookingsLoadService.getBookingByProduct(productId);
            expect(bookingsMock.get).toHaveBeenCalled();
        });

        it("BookingsLoadService:requestBooking", function () {
            var booking = {};
            BookingsLoadService.requestBooking(booking);
            expect(bookingsMock.save).toHaveBeenCalledWith(booking);
        });

        it("BookingsLoadService:payForBooking", function () {
            var uuid = 1, paymentInfo = {};
            BookingsLoadService.payForBooking(uuid, paymentInfo);
            expect(bookingsMock.pay).toHaveBeenCalledWith({uuid: uuid}, paymentInfo);
        });
    });
});