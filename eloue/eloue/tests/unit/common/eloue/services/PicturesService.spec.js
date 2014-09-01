define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: PicturesService", function () {

        var PicturesService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_PicturesService_) {
            PicturesService = _PicturesService_;
        }));

        it("PicturesService should be not null", function () {
            expect(!!PicturesService).toBe(true);
        });
    });
});