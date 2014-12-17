define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsLoadService", function () {

        var CommentsLoadService,
            q,
            commentsMock,
            endpointsMock,
            usersServiceMock,
            utilsServiceMock,
            commentsParseServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            commentsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
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
            commentsParseServiceMock = {
                parseComment: function (commentData, authorData) {

                }
            };

            module(function ($provide) {
                $provide.value("Comments", commentsMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("CommentsParseService", commentsParseServiceMock);
            });
        });

        beforeEach(inject(function (_CommentsLoadService_, $q) {
            CommentsLoadService = _CommentsLoadService_;
            q= $q;
            spyOn(commentsMock, "get").and.callThrough();
            spyOn(commentsMock, "save").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(commentsParseServiceMock, "parseComment").and.callThrough();
        }));

        it("CommentsLoadService should be not null", function () {
            expect(!!CommentsLoadService).toBe(true);
        });

        it("CommentsLoadService:getCommentList", function () {
            var uuid = 1;
            CommentsLoadService.getCommentList(uuid);
        });

        it("CommentsLoadService:postComment", function () {
            var uuid = 1, comment = "msg", rate = 5;
            CommentsLoadService.postComment(uuid, comment, rate);
        });
    });
});