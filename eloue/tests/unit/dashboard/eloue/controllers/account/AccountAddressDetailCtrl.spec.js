define(["angular-mocks", "eloue/controllers/account/AccountAddressDetailCtrl"], function () {

    describe("Controller: AccountAddressDetailCtrl", function () {

        var AccountAddressDetailCtrl,
            scope,
            stateParams,
            addressesServiceMock,
            productsServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {

            addressesServiceMock = {
                getAddress: function (addressId) {
                    console.log("addressesServiceMock:getAddress called with addressId = " + addressId);
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                updateAddress: function (addressId, formData) {
                    console.log("addressesServiceMock:updateAddress called with addressId = " + addressId + ", formData = " + formData);
                    return {then: function () {
                        return {result: {}}
                    }}
                },
                deleteAddress: function (addressId) {
                    console.log("addressesServiceMock:deleteAddress called with addressId = " + addressId);
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            productsServiceMock = {
                getProductsByAddress: function (addressId) {
                    console.log("productsServiceMock:getProductsByAddress called with addressId = " + addressId);
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };

            module(function ($provide) {
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("ProductsService", productsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {
                id: 1
            };
            spyOn(addressesServiceMock, "getAddress").and.callThrough();
            spyOn(addressesServiceMock, "updateAddress").and.callThrough();
            spyOn(addressesServiceMock, "deleteAddress").and.callThrough();
            spyOn(productsServiceMock, "getProductsByAddress").and.callThrough();

            AccountAddressDetailCtrl = $controller('AccountAddressDetailCtrl', { $scope: scope, $stateParams: stateParams, AddressesService: addressesServiceMock, ProductsService: productsServiceMock });
        }));

        it("AccountAddressDetailCtrl should be not null", function () {
            expect(!!AccountAddressDetailCtrl).toBe(true);
        });

        it("AccountAddressDetailCtrl:submitAddress", function () {
            scope.submitAddress();
            expect(addressesServiceMock.updateAddress).toHaveBeenCalled();
        });

        it("AccountAddressDetailCtrl:deleteAddress", function () {
            scope.deleteAddress();
            expect(addressesServiceMock.deleteAddress).toHaveBeenCalled();
        });
    });
});