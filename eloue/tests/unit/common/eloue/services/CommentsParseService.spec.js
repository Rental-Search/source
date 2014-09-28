define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsParseService", function () {

        var CommentsParseService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_CommentsParseService_) {
            CommentsParseService = _CommentsParseService_;
        }));

        it("CommentsParseService should be not null", function () {
            expect(!!CommentsParseService).toBe(true);
        });

        it("CommentsParseService:parseComment", function () {
            var author = "Author";
            var result = CommentsParseService.parseComment({}, author);
            expect(result).toEqual({author: author});
        });
    });
});
