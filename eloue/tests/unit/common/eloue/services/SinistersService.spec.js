define(["angular-mocks", "eloue/services/SinistersService"], function () {

    describe("Service: SinistersService", function () {

        var SinistersService,
            sinistersMock,
            endpointsMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            sinistersMock = {
                get: function () {
                    return simpleResourceResponse;
                }
            };
            endpointsMock = {
            };
            module(function ($provide) {
                $provide.value("Sinisters", sinistersMock);
                $provide.value("Endpoints", endpointsMock);
            });
        });

        beforeEach(inject(function (_SinistersService_) {
            SinistersService = _SinistersService_;
            spyOn(sinistersMock, "get").and.callThrough();
        }));

        it("SinistersService should be not null", function () {
            expect(!!SinistersService).toBe(true);
        });

        it("SinistersService:getSinisterList", function () {
            var bookingUUID = 1;
            SinistersService.getSinisterList(bookingUUID);
            expect(sinistersMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number), booking: bookingUUID});
        });
    });
});