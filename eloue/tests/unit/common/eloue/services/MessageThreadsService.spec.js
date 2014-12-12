define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsService", function () {

        var MessageThreadsService,
            q,
            messageThreadsMock,
            productRelatedMessagesServiceMock,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            messageThreadsMock = {
                list: function () {
                    return {$promise: {then: function () {
                        return {results: [
                            {messages: [
                                "http://10.0.0.111:8000/api/2.0/productrelatedmessages/28394/"
                            ]}
                        ]}
                    }}}
                }
            };
            productRelatedMessagesServiceMock = {
                getMessage: function (messageId) {
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
                $provide.value("ProductRelatedMessagesService", productRelatedMessagesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_MessageThreadsService_, $q) {
            q = $q;
            MessageThreadsService = _MessageThreadsService_;
            spyOn(messageThreadsMock, "list").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "getMessage").and.callThrough();
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
        }));

        it("MessageThreadsService should be not null", function () {
            expect(!!MessageThreadsService).toBe(true);
        });

        it("MessageThreadsService:getMessageThread", function () {
            var productId = 1, participantId = 2;
            MessageThreadsService.getMessageThread(productId, participantId);
            expect(messageThreadsMock.list).toHaveBeenCalledWith({product: productId, participant: participantId, _cache: jasmine.any(Number)});
        });
    });
});
