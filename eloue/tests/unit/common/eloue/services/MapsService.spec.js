define(["angular-mocks", "eloue/services/MapsService"], function () {

    describe("Service: MapsService", function () {

        var MapsService,
            document;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
                $provide.value("$document", document);
            });
        });

        beforeEach(inject(function (_MapsService_) {
            MapsService = _MapsService_;
        }));

        it("MapsService should be not null", function () {
            expect(!!MapsService).toBe(true);
        });

        it("MapsService:range", function () {
            var result = MapsService.range(14);
            expect(result).toEqual(0.5);
        });

        it("MapsService:zoom", function () {
            var result = MapsService.zoom(0.5);
            expect(result).toEqual(14);
        });
    });
});
