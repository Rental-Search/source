define(["angular-mocks", "eloue/services/ShippingPointsService"], function () {

    describe("Service: ShippingPointsService", function () {

        var ShippingPointsService,
            shippingPointsMock,
            productsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            shippingPointsMock = {
                get: function () {
                    return {$promise: {}}
                }
            };
            productsMock = {
                getShippingPoints:  function () {
                    return {$promise: {}}
                }
            };
            module(function ($provide) {
                $provide.value("ShippingPoints", shippingPointsMock);
                $provide.value("Products", productsMock);
            });
        });

        beforeEach(inject(function (_ShippingPointsService_) {
            ShippingPointsService = _ShippingPointsService_;
            spyOn(shippingPointsMock, "get").and.callThrough();
            spyOn(productsMock, "getShippingPoints").and.callThrough();
        }));

        it("ShippingPointsService should be not null", function () {
            expect(!!ShippingPointsService).toBe(true);
        });

        it("ShippingPointsService:searchArrivalShippingPointsByCoordinatesAndProduct", function () {
            var lat = 1, lng = 1, productId = 1;
            ShippingPointsService.searchArrivalShippingPointsByCoordinatesAndProduct(lat, lng, productId);
            expect(productsMock.getShippingPoints).toHaveBeenCalledWith({id: productId, lat: lat, lng: lng, search_type: 2, _cache: jasmine.any(Number)});
        });

        it("ShippingPointsService:searchArrivalShippingPointsByAddressAndProduct", function () {
            var address = {}, productId = 1;
            ShippingPointsService.searchArrivalShippingPointsByAddressAndProduct(address, productId);
            expect(productsMock.getShippingPoints).toHaveBeenCalledWith({id: productId, address: address, search_type: 2, _cache: jasmine.any(Number)});
        });

        it("ShippingPointsService:searchShippingPointsByCoordinates", function () {
            var lat = 1, lng = 1, searchType = 1;
            ShippingPointsService.searchShippingPointsByCoordinates(lat, lng, searchType);
            expect(shippingPointsMock.get).toHaveBeenCalledWith({lat: lat, lng: lng, search_type: searchType, _cache: jasmine.any(Number)});
        });

        it("ShippingPointsService:searchShippingPointsByAddress", function () {
            var address = {}, searchType = 1;
            ShippingPointsService.searchShippingPointsByAddress(address, searchType);
            expect(shippingPointsMock.get).toHaveBeenCalledWith({address: address, search_type: searchType, _cache: jasmine.any(Number)});
        });

        it("ShippingPointsService:searchDepartureShippingPointsByAddress", function () {
            var address = {};
            ShippingPointsService.searchDepartureShippingPointsByAddress(address);
        });

        it("ShippingPointsService:searchDepartureShippingPointsByCoordinates", function () {
            var lat = 1, lng = 1;
            ShippingPointsService.searchDepartureShippingPointsByCoordinates(lat, lng);
        });

        it("ShippingPointsService:searchArrivalShippingPointsByAddress", function () {
            var address = {};
            ShippingPointsService.searchArrivalShippingPointsByAddress(address);
        });

        it("ShippingPointsService:searchArrivalShippingPointsByCoordinates", function () {
            var lat = 1, lng = 1;
            ShippingPointsService.searchArrivalShippingPointsByCoordinates(lat, lng);
        });
    });
});