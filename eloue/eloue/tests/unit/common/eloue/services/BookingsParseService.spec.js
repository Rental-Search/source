define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsParseService", function () {

        var BookingsParseService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_BookingsParseService_) {
            BookingsParseService = _BookingsParseService_;
        }));

        it("BookingsParseService should be not null", function () {
            expect(!!BookingsParseService).toBe(true);
        });
    });
});