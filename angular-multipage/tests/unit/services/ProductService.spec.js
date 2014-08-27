define(["angular-mocks", "eloue/modules/booking/services/ProductService"], function () {

    describe("Service: ProductService", function () {

        var ProductService, usersResourceMock, productsResourceMock, checkAvailabilityResourceMock, phoneNumbersResourceMock, addressesResourceMock;

        beforeEach(module("EloueApp"));

        beforeEach(function () {
            usersResourceMock = {get: function () {
            }};
            productsResourceMock = {get: function () {
                return {$promise: {
                    then: function () {
                    }
                }
                }
            }};
            checkAvailabilityResourceMock = {get: function () {
            }};
            phoneNumbersResourceMock = {get: function () {
            }};
            addressesResourceMock = {get: function () {
            }};

            module(function ($provide) {
                $provide.value("Users", usersResourceMock);
                $provide.value("Products", productsResourceMock);
                $provide.value("CheckAvailability", checkAvailabilityResourceMock);
                $provide.value("PhoneNumbers", phoneNumbersResourceMock);
                $provide.value("Addresses", addressesResourceMock);
            });
        });

        beforeEach(inject(function (_ProductService_) {
            ProductService = _ProductService_;
            spyOn(usersResourceMock, "get").andCallThrough();
            spyOn(productsResourceMock, "get").andCallThrough();
            spyOn(checkAvailabilityResourceMock, "get").andCallThrough();
            spyOn(phoneNumbersResourceMock, "get").andCallThrough();
            spyOn(addressesResourceMock, "get").andCallThrough();
        }));

        it("ProductService should be not null", function () {
            expect(!!ProductService).toBe(true);
        });

        it("ProductService should have a getUser function", function () {
            expect(angular.isFunction(ProductService.getProduct)).toBe(true);
            expect(angular.isFunction(ProductService.isAvailable)).toBe(true);
            expect(angular.isFunction(ProductService.getIdFromUrl)).toBe(true);
        });

        it("ProductService getProduct", function () {
            var productId = 1;
            ProductService.getProduct(productId);
            expect(productsResourceMock.get).toHaveBeenCalledWith({id: productId});
        });

        it("ProductService isAvailable", function () {
            var productId = 1, startDate = "22/07/2014+08:00", endDate = "23/07/2014+08:00", quantity = 1;
            ProductService.isAvailable(productId, startDate, endDate, quantity);
            expect(checkAvailabilityResourceMock.get).toHaveBeenCalledWith({id: productId, started_at: startDate, ended_at: endDate, quantity: quantity});
        });
    });
});
