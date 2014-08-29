define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsService", function () {

        var BookingsService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_BookingsService_) {
            BookingsService = _BookingsService_;
        }));

        it("BookingsService should be not null", function () {
            expect(!!BookingsService).toBe(true);
        });
    });
});