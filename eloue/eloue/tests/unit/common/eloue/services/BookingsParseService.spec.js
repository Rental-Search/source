define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsParseService", function () {

        var BookingsParseService,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            utilsServiceMock = {
                formatDate: function (date, format) {

                }
            };
            module(function ($provide) {
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_BookingsParseService_) {
            BookingsParseService = _BookingsParseService_;
            spyOn(utilsServiceMock, "formatDate").andCallThrough();
        }));

        it("BookingsParseService should be not null", function () {
            expect(!!BookingsParseService).toBe(true);
        });
    });
});