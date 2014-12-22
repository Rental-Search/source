define(["angular-mocks", "eloue/services/BookingsService"], function () {

    describe("Service: BookingsService", function () {

        var BookingsService,
            q,
            endpointsMock,
            bookingsMock,
            utilsServiceMock,
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
                downloadPdfFile: function(url) {},
                formatDate: function (date, format) {

                },
                calculatePeriodBetweenDates: function(firstDate, secondDate) {
                    return {}
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
                $provide.value("MessageThreadsService", messageThreadsServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsService_, $q) {
            BookingsService = _BookingsService_;
            q = $q;
            spyOn(bookingsMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
            spyOn(utilsServiceMock, "calculatePeriodBetweenDates").and.callThrough();
            spyOn(bookingsMock, "save").and.callThrough();
            spyOn(bookingsMock, "pay").and.callThrough();
            spyOn(bookingsMock, "incident").and.callThrough();
            spyOn(bookingsMock, "accept").and.callThrough();
            spyOn(bookingsMock, "cancel").and.callThrough();
            spyOn(bookingsMock, "reject").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(utilsServiceMock, "downloadPdfFile").and.callThrough();
            spyOn(messageThreadsServiceMock, "getMessageThread").and.callThrough();
        }));

        it("BookingsService should be not null", function () {
            expect(!!BookingsService).toBe(true);
        });

        it("BookingsService:getBookingsByProduct", function () {
            var productId = 1;
            BookingsService.getBookingsByProduct(productId);
            expect(bookingsMock.get).toHaveBeenCalledWith({product: productId, _cache: jasmine.any(Number)});
        });

        it("BookingsService:getBookingList", function () {
            var author, state, borrowerId, ownerId, page;
            BookingsService.getBookingList(author, state, borrowerId, ownerId, page);
            expect(bookingsMock.get).toHaveBeenCalled();
        });

        it("BookingsService:getBooking", function () {
            var uuid = 1;
            BookingsService.getBooking(uuid);
            expect(bookingsMock.get).toHaveBeenCalledWith({uuid: uuid, _cache: jasmine.any(Number)});
        });

        it("BookingsService:getBookingDetails", function () {
            var uuid = 1;
            BookingsService.getBookingDetails(uuid);
        });

        it("BookingsService:acceptBooking", function () {
            var uuid = 1;
            BookingsService.acceptBooking(uuid);
            expect(bookingsMock.accept).toHaveBeenCalledWith({uuid: uuid}, {uuid: uuid});
        });

        it("BookingsService:cancelBooking", function () {
            var uuid = 1;
            BookingsService.cancelBooking(uuid);
            expect(bookingsMock.cancel).toHaveBeenCalledWith({uuid: uuid}, {uuid: uuid});
        });

        it("BookingsService:rejectBooking", function () {
            var uuid = 1;
            BookingsService.rejectBooking(uuid);
            expect(bookingsMock.reject).toHaveBeenCalledWith({uuid: uuid}, {uuid: uuid});
        });

        it("BookingsService:postIncident", function () {
            var uuid = 1, description = "";
            BookingsService.postIncident(uuid, description);
            expect(bookingsMock.incident).toHaveBeenCalledWith({uuid: uuid}, {description: description});
        });

        it("BookingsService:downloadContract", function () {
            var uuid = 1;
            BookingsService.downloadContract(uuid);
            expect(utilsServiceMock.downloadPdfFile).toHaveBeenCalled();
        });

        it("BookingsService:getBookingByProduct", function () {
            var productId = 1;
            BookingsService.getBookingByProduct(productId);
            expect(bookingsMock.get).toHaveBeenCalled();
        });

        it("BookingsService:requestBooking", function () {
            var booking = {};
            BookingsService.requestBooking(booking);
            expect(bookingsMock.save).toHaveBeenCalledWith(booking);
        });

        it("BookingsService:payForBooking", function () {
            var uuid = 1, paymentInfo = {};
            BookingsService.payForBooking(uuid, paymentInfo);
            expect(bookingsMock.pay).toHaveBeenCalledWith({uuid: uuid}, paymentInfo);
        });

        it("BookingsService:parseBookingListItem", function () {
            var bookingData = {}, productData = {}, picturesDataArray = [{image: {thumbnail: "111.png"}}];
            var result = BookingsService.parseBookingListItem(bookingData, productData, picturesDataArray);
            expect(result.picture).toEqual(picturesDataArray[0].image.thumbnail);
        });
        it("BookingsService:parseBooking", function () {
            var bookingData = {id: 1};
            var result = BookingsService.parseBooking(bookingData);
            expect(result.id).toEqual(bookingData.id);
        });
    });
});