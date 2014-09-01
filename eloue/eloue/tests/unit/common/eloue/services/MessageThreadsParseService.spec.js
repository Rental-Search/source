define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsParseService", function () {

        var MessageThreadsParseService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_MessageThreadsParseService_) {
            MessageThreadsParseService = _MessageThreadsParseService_;
        }));

        it("MessageThreadsParseService should be not null", function () {
            expect(!!MessageThreadsParseService).toBe(true);
        });
    });
});

