define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsParseService", function () {

        var MessageThreadsParseService,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            utilsServiceMock = {
                formatDate: function (date, format) {
                }
            };

            module(function ($provide) {
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_MessageThreadsParseService_) {
            MessageThreadsParseService = _MessageThreadsParseService_;
            spyOn(utilsServiceMock, "formatDate").andCallThrough();
        }));

        it("MessageThreadsParseService should be not null", function () {
            expect(!!MessageThreadsParseService).toBe(true);
        });
    });
});

