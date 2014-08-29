define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CategoriesService", function () {

        var CategoriesService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_CategoriesService_) {
            CategoriesService = _CategoriesService_;
        }));

        it("CategoriesService should be not null", function () {
            expect(!!CategoriesService).toBe(true);
        });
    });
});