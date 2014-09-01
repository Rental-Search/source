define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: BookingsLoadService", function () {

        var BookingsLoadService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_BookingsLoadService_) {
            BookingsLoadService = _BookingsLoadService_;
        }));

        it("BookingsLoadService should be not null", function () {
            expect(!!BookingsLoadService).toBe(true);
        });
    });
});