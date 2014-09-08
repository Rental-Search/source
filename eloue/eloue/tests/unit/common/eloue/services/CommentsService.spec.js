define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsService", function () {

        var CommentsService,
            commentsMock,
            endpointsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            commentsMock = {
                get: function () {
                    return {$promise: {}}
                },
                save: function () {
                }
            };
            endpointsMock = {
            };
            module(function ($provide) {
                $provide.value("Comments", commentsMock);
                $provide.value("Endpoints", endpointsMock);
            });
        });

        beforeEach(inject(function (_CommentsService_) {
            CommentsService = _CommentsService_;
            spyOn(commentsMock, "get").andCallThrough();
            spyOn(commentsMock, "save").andCallThrough();
        }));

        it("CommentsService should be not null", function () {
            expect(!!CommentsService).toBe(true);
        });

        it("CommentsService:getCommentList", function () {
            var bookingUUID = 1;
            CommentsService.getCommentList(bookingUUID);
            expect(commentsMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number), booking: bookingUUID});
        });

        it("CommentsService:postComment", function () {
            var bookingUUID = 1, comment = "Comment", rate = 5;
            CommentsService.postComment(bookingUUID, comment, rate);
            expect(commentsMock.save).toHaveBeenCalledWith({
                booking: jasmine.any(String),
                comment: comment,
                rate: rate
            });
        });
    });
});