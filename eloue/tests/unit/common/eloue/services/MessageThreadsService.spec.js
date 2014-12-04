define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsService", function () {

        var MessageThreadsService,
            messageThreadsMock,
            bookingsMock,
            productRelatedMessagesServiceMock,
            usersServiceMock,
            productsServiceMock,
            bookingsServiceMock,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            messageThreadsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: [
                            {messages: [
                                "http://10.0.0.111:8000/api/2.0/productrelatedmessages/28394/"
                            ]}
                        ]}
                    }}}
                }
            };
            bookingsMock = {};
            productRelatedMessagesServiceMock = {
                getMessage: function (messageId) {
                }
            };
            usersServiceMock = {
                get: function (userId) {
                }
            };
            productsServiceMock = {
            };
            bookingsServiceMock = {
                getBookingDetailProduct: function (productId) {
                }
            };
            utilsServiceMock = {
                formatDate: function (date, format) {
                },
                getIdFromUrl: function (url) {
                }
            };

            module(function ($provide) {
                $provide.value("MessageThreads", messageThreadsMock);
                $provide.value("Bookings", bookingsMock);
                $provide.value("ProductRelatedMessagesService", productRelatedMessagesServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_MessageThreadsService_) {
            MessageThreadsService = _MessageThreadsService_;
            spyOn(messageThreadsMock, "get").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessage").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(bookingsServiceMock, "getBookingDetailProduct").and.callThrough();
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
        }));

        it("MessageThreadsService should be not null", function () {
            expect(!!MessageThreadsService).toBe(true);
        });
    });
});
