define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsService", function () {

        var CommentsService,
            q,
            commentsMock,
            endpointsMock,
            usersServiceMock,
            utilsServiceMock;

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

            usersServiceMock = {
                get: function (userId) {
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {

                }
            };
            module(function ($provide) {
                $provide.value("Comments", commentsMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_CommentsService_, $q) {
            CommentsService = _CommentsService_;
            q= $q;
            spyOn(commentsMock, "get").and.callThrough();
            spyOn(commentsMock, "save").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(commentsParseServiceMock, "parseComment").and.callThrough();
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

        it("CommentsService:parseComment", function () {
            var author = "Author";
            var result = CommentsService.parseComment({}, author);
            expect(result).toEqual({author: author});
        });
    });
});