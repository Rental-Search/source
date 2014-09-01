define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProAgenciesService", function () {

        var ProAgenciesService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_ProAgenciesService_) {
            ProAgenciesService = _ProAgenciesService_;
        }));

        it("ProAgenciesService should be not null", function () {
            expect(!!ProAgenciesService).toBe(true);
        });
    });
});