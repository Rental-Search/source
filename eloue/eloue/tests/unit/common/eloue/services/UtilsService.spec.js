define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: UtilsService", function () {

        var UtilsService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_UtilsService_) {
            UtilsService = _UtilsService_;
        }));

        it("UtilsService should be not null", function () {
            expect(!!UtilsService).toBe(true);
        });
    });
});
