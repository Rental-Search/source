define(["angular-mocks", "eloue/services/PricesService"], function () {

    describe("Service: PricesService", function () {

        var PricesService,
            pricesMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            pricesMock = {
                save: function () {
                    return simpleResourceResponse;
                },
                update: function () {
                    return simpleResourceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("Prices", pricesMock);
            });
        });

        beforeEach(inject(function (_PricesService_) {
            PricesService = _PricesService_;
            spyOn(pricesMock, "save").and.callThrough();
            spyOn(pricesMock, "update").and.callThrough();
        }));

        it("PricesService should be not null", function () {
            expect(!!PricesService).toBe(true);
        });

        it("PricesService:savePrice", function () {
            var price = {id: 1};
            PricesService.savePrice(price);
            expect(pricesMock.save).toHaveBeenCalledWith(price);
        });

        it("PricesService:updatePrice", function () {
            var price = {id: 1};
            PricesService.updatePrice(price);
            expect(pricesMock.update).toHaveBeenCalledWith({id: price.id}, price);
        });
    });
});