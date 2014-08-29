define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsLoadService", function () {

        var CommentsLoadService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_CommentsLoadService_) {
            CommentsLoadService = _CommentsLoadService_;
        }));

        it("CommentsLoadService should be not null", function () {
            expect(!!CommentsLoadService).toBe(true);
        });
    });
});