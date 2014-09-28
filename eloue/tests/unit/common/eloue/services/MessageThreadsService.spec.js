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
            spyOn(messageThreadsMock, "get").andCallThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessage").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(bookingsServiceMock, "getBookingDetailProduct").andCallThrough();
            spyOn(utilsServiceMock, "formatDate").andCallThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").andCallThrough();
        }));

        it("MessageThreadsService should be not null", function () {
            expect(!!MessageThreadsService).toBe(true);
        });

        it("MessageThreadsService:getMessageThreads", function () {
            MessageThreadsService.getMessageThreads();
            expect(messageThreadsMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number)});
        });

        it("MessageThreadsService:getThread", function () {
            var threadId = 1;
            MessageThreadsService.getThread(threadId);
            expect(messageThreadsMock.get).toHaveBeenCalledWith({id: threadId, _cache: jasmine.any(Number)});
        });

        it("MessageThreadsService:getMessages", function () {
            var threadId = 1;
            MessageThreadsService.getMessages(threadId);
            expect(messageThreadsMock.get).toHaveBeenCalledWith({id: threadId,_cache: jasmine.any(Number)});
        });
    });
});
