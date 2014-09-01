define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CommentsService", function () {

        var CommentsService,
            commentsMock,
            endpointsMock;

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
    });
});