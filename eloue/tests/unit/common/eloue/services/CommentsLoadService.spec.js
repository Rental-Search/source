define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsLoadService", function () {

        var CommentsLoadService,
            commentsMock,
            endpointsMock,
            usersServiceMock,
            utilsServiceMock,
            commentsParseServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            commentsMock = {
                get: function () {
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

        beforeEach(inject(function (_CommentsLoadService_) {
            CommentsLoadService = _CommentsLoadService_;
            spyOn(commentsMock, "get").and.callThrough();
            spyOn(commentsMock, "save").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(commentsParseServiceMock, "parseComment").and.callThrough();
        }));

        it("CommentsLoadService should be not null", function () {
            expect(!!CommentsLoadService).toBe(true);
        });
    });
});