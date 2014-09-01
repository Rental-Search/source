define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsService", function () {

        var CommentsService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_CommentsService_) {
            CommentsService = _CommentsService_;
        }));

        it("CommentsService should be not null", function () {
            expect(!!CommentsService).toBe(true);
        });
    });
});