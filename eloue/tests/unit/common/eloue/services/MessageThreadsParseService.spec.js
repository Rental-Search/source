define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsParseService", function () {

        var MessageThreadsParseService,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            utilsServiceMock = {
                formatDate: function (date, format) {
                },
                isToday: function(date) {

                }
            };

            module(function ($provide) {
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_MessageThreadsParseService_) {
            MessageThreadsParseService = _MessageThreadsParseService_;
            spyOn(utilsServiceMock, "formatDate").and.callThrough();
        }));

        it("MessageThreadsParseService should be not null", function () {
            expect(!!MessageThreadsParseService).toBe(true);
        });

        it("MessageThreadsParseService:parseMessageThreadListItem", function () {
            var messageThreadData = { messages: [{id:1}], last_message: {sent_at: "2014-11-29 12:00:00"}}, lastMessageData = {};
            MessageThreadsParseService.parseMessageThreadListItem(messageThreadData, lastMessageData);
        });

        it("MessageThreadsParseService:parseMessageThread", function () {
            var messageThreadData = { messages: [{id:""}]}, messagesDataArray = [], productData = {id: 1};
            MessageThreadsParseService.parseMessageThread(messageThreadData, messagesDataArray, productData);
        });
    });
});

