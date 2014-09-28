define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: FormService", function () {

        var FormService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_FormService_) {
            FormService = _FormService_;
        }));

        it("FormService should be not null", function () {
            expect(!!FormService).toBe(true);
        });
    });
});
