define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsService", function () {

        var MessageThreadsService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_MessageThreadsService_) {
            MessageThreadsService = _MessageThreadsService_;
        }));

        it("MessageThreadsService should be not null", function () {
            expect(!!MessageThreadsService).toBe(true);
        });
    });
});
