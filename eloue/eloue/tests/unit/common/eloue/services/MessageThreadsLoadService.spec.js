define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: MessageThreadsLoadService", function () {

        var MessageThreadsLoadService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_MessageThreadsLoadService_) {
            MessageThreadsLoadService = _MessageThreadsLoadService_;
        }));

        it("MessageThreadsLoadService should be not null", function () {
            expect(!!MessageThreadsLoadService).toBe(true);
        });
    });
});